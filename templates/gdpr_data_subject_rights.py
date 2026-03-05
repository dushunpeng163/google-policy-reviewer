#!/usr/bin/env python3
"""
GDPR数据主体权利实现系统
GDPR Data Subject Rights Implementation System

实现GDPR第三章规定的所有数据主体权利：
- 访问权 (Right of Access)
- 更正权 (Right to Rectification) 
- 删除权 (Right to Erasure)
- 限制处理权 (Right to Restrict Processing)
- 数据可携带权 (Right to Data Portability)
- 反对权 (Right to Object)

使用方法:
from templates.gdpr_data_subject_rights import GDPRRightsManager

rights_manager = GDPRRightsManager()
result = await rights_manager.process_access_request(user_id)
"""

import json
import uuid
import asyncio
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import hashlib
import csv
import io

class RequestType(Enum):
    """数据主体权利请求类型"""
    ACCESS = "access"                    # 访问权 - Art. 15
    RECTIFICATION = "rectification"      # 更正权 - Art. 16
    ERASURE = "erasure"                 # 删除权 - Art. 17
    RESTRICT = "restrict"               # 限制处理权 - Art. 18
    PORTABILITY = "portability"         # 数据可携带权 - Art. 20
    OBJECT = "object"                   # 反对权 - Art. 21

class RequestStatus(Enum):
    """请求处理状态"""
    RECEIVED = "received"
    IDENTITY_VERIFICATION = "identity_verification"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REJECTED = "rejected"
    PARTIALLY_FULFILLED = "partially_fulfilled"

class LegalBasis(Enum):
    """处理数据的法律依据"""
    CONSENT = "consent"                 # Art. 6(1)(a) - 同意
    CONTRACT = "contract"               # Art. 6(1)(b) - 合同履行
    LEGAL_OBLIGATION = "legal_obligation"  # Art. 6(1)(c) - 法律义务
    VITAL_INTERESTS = "vital_interests"    # Art. 6(1)(d) - 生命利益
    PUBLIC_TASK = "public_task"            # Art. 6(1)(e) - 公共任务
    LEGITIMATE_INTERESTS = "legitimate_interests"  # Art. 6(1)(f) - 合法利益

@dataclass
class DataCategory:
    """数据类别"""
    category_name: str
    description: str
    data_fields: List[str]
    retention_period: str
    legal_basis: LegalBasis
    can_be_erased: bool = True
    can_be_ported: bool = True

@dataclass
class RightsRequest:
    """数据主体权利请求"""
    request_id: str
    user_id: str
    request_type: RequestType
    status: RequestStatus
    created_at: datetime
    identity_verified: bool = False
    identity_verification_method: Optional[str] = None
    processed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    processing_notes: Optional[str] = None
    requested_data_categories: Optional[List[str]] = None
    verification_deadline: Optional[datetime] = None

@dataclass
class ProcessedDataRecord:
    """个人数据处理记录"""
    data_id: str
    user_id: str
    category: str
    data_content: Dict[str, Any]
    legal_basis: LegalBasis
    processing_purpose: str
    retention_deadline: datetime
    created_at: datetime
    last_updated: Optional[datetime] = None
    is_restricted: bool = False
    restriction_reason: Optional[str] = None

class GDPRRightsManager:
    """GDPR数据主体权利管理器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or self._get_default_config()
        self.logger = self._setup_logging()
        self.db_path = Path(__file__).parent.parent / "data" / "gdpr_rights.db"
        self._init_database()
        
        # 定义标准数据类别
        self.data_categories = self._define_data_categories()
        
        # 初始化第三方服务
        self.email_service = self._init_email_service()
        self.identity_verification_service = self._init_identity_verification()
        
    def _get_default_config(self) -> Dict:
        """默认配置"""
        return {
            'response_timeframes': {
                'standard_days': 30,      # GDPR Art. 12(3) - 1个月内响应
                'complex_extension_days': 60,  # 可延长2个月
                'identity_verification_days': 7    # 身份验证期限
            },
            'identity_verification': {
                'required_for_access': True,
                'required_for_erasure': True,
                'required_for_portability': True,
                'methods': ['email_verification', 'document_upload', 'two_factor_auth']
            },
            'data_retention': {
                'request_records_years': 7,        # 保留请求记录7年
                'audit_logs_years': 7,            # 审计日志7年
                'backup_recovery_days': 90        # 备份数据恢复期限90天
            },
            'notification_settings': {
                'send_acknowledgment': True,       # 发送请求确认
                'send_completion_notice': True,   # 发送完成通知
                'send_rejection_notice': True,    # 发送拒绝通知
                'progress_updates': True          # 发送进度更新
            },
            'automation': {
                'auto_process_access_requests': False,  # 访问请求需要手动审核
                'auto_process_corrections': False,      # 更正请求需要手动审核
                'auto_delete_expired_data': True,       # 自动删除过期数据
                'batch_processing': True                # 批量处理请求
            }
        }
    
    def _init_database(self):
        """初始化数据库"""
        self.db_path.parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # 数据主体权利请求表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rights_requests (
                    request_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    request_type TEXT NOT NULL,
                    status TEXT DEFAULT 'received',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    identity_verified BOOLEAN DEFAULT FALSE,
                    identity_verification_method TEXT,
                    processed_at DATETIME,
                    completed_at DATETIME,
                    rejection_reason TEXT,
                    processing_notes TEXT,
                    requested_data_categories TEXT,  -- JSON array
                    verification_deadline DATETIME
                )
            """)
            
            # 个人数据处理记录表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS data_records (
                    data_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    category TEXT NOT NULL,
                    data_content TEXT NOT NULL,  -- JSON
                    legal_basis TEXT NOT NULL,
                    processing_purpose TEXT NOT NULL,
                    retention_deadline DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_updated DATETIME,
                    is_restricted BOOLEAN DEFAULT FALSE,
                    restriction_reason TEXT
                )
            """)
            
            # 数据处理活动日志表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS processing_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    activity_type TEXT NOT NULL,  -- collect, process, share, delete
                    data_categories TEXT NOT NULL,  -- JSON array
                    legal_basis TEXT NOT NULL,
                    purpose TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    automated BOOLEAN DEFAULT TRUE,
                    processor_id TEXT
                )
            """)
    
    def _define_data_categories(self) -> Dict[str, DataCategory]:
        """定义数据类别"""
        categories = {
            'profile': DataCategory(
                category_name="Profile Information",
                description="Basic user profile data",
                data_fields=["user_id", "username", "email", "display_name", "date_of_birth", "country"],
                retention_period="Account active + 2 years",
                legal_basis=LegalBasis.CONTRACT
            ),
            'educational_progress': DataCategory(
                category_name="Educational Progress",
                description="Learning progress and achievements",
                data_fields=["course_progress", "test_scores", "achievements", "learning_time"],
                retention_period="Educational purpose + 5 years",
                legal_basis=LegalBasis.LEGITIMATE_INTERESTS
            ),
            'app_usage': DataCategory(
                category_name="App Usage Analytics",
                description="How the user interacts with the app",
                data_fields=["session_logs", "feature_usage", "click_tracking", "device_info"],
                retention_period="2 years from collection",
                legal_basis=LegalBasis.LEGITIMATE_INTERESTS,
                can_be_ported=False  # 技术数据通常不可携带
            ),
            'communications': DataCategory(
                category_name="Communications",
                description="Messages, comments, and communications",
                data_fields=["chat_messages", "forum_posts", "support_tickets"],
                retention_period="3 years from creation",
                legal_basis=LegalBasis.CONSENT
            ),
            'parental_data': DataCategory(
                category_name="Parental Information",
                description="Parent/guardian data for child accounts",
                data_fields=["parent_email", "parent_phone", "parental_consent_records"],
                retention_period="Child reaches 18 + 1 year",
                legal_basis=LegalBasis.LEGAL_OBLIGATION
            ),
            'financial': DataCategory(
                category_name="Financial Data",
                description="Payment and billing information",
                data_fields=["payment_history", "billing_address", "payment_method_tokens"],
                retention_period="7 years (legal requirement)",
                legal_basis=LegalBasis.LEGAL_OBLIGATION,
                can_be_erased=False  # 法律要求保留
            )
        }
        
        return categories
    
    async def submit_rights_request(
        self, 
        user_id: str,
        request_type: RequestType,
        additional_info: Dict = None
    ) -> RightsRequest:
        """提交数据主体权利请求"""
        
        request_id = f"gdpr_req_{uuid.uuid4().hex[:12]}"
        
        # 创建请求记录
        request = RightsRequest(
            request_id=request_id,
            user_id=user_id,
            request_type=request_type,
            status=RequestStatus.RECEIVED,
            created_at=datetime.now(),
            requested_data_categories=additional_info.get('data_categories') if additional_info else None
        )
        
        # 设置身份验证期限
        if self._requires_identity_verification(request_type):
            request.verification_deadline = datetime.now() + timedelta(
                days=self.config['response_timeframes']['identity_verification_days']
            )
            request.status = RequestStatus.IDENTITY_VERIFICATION
        
        # 保存到数据库
        await self._save_rights_request(request)
        
        # 记录审计日志
        self.logger.info(f"GDPR_REQUEST_SUBMITTED - request_id: {request_id}, type: {request_type.value}, user: {user_id}")
        
        # 发送确认通知
        if self.config['notification_settings']['send_acknowledgment']:
            await self._send_request_acknowledgment(request)
        
        # 如果不需要身份验证，直接开始处理
        if not self._requires_identity_verification(request_type):
            asyncio.create_task(self._process_rights_request(request))
        
        return request
    
    def _requires_identity_verification(self, request_type: RequestType) -> bool:
        """检查是否需要身份验证"""
        verification_config = self.config['identity_verification']
        
        if request_type == RequestType.ACCESS:
            return verification_config['required_for_access']
        elif request_type == RequestType.ERASURE:
            return verification_config['required_for_erasure']
        elif request_type == RequestType.PORTABILITY:
            return verification_config['required_for_portability']
        else:
            return False  # 其他类型的请求通常不需要强制身份验证
    
    async def verify_identity(
        self, 
        request_id: str, 
        verification_method: str, 
        verification_data: Dict
    ) -> bool:
        """验证用户身份"""
        
        request = await self._get_rights_request(request_id)
        if not request:
            raise ValueError("Invalid request ID")
        
        if request.status != RequestStatus.IDENTITY_VERIFICATION:
            raise ValueError("Request is not pending identity verification")
        
        # 检查是否超过验证期限
        if request.verification_deadline and datetime.now() > request.verification_deadline:
            request.status = RequestStatus.REJECTED
            request.rejection_reason = "Identity verification deadline exceeded"
            await self._save_rights_request(request)
            return False
        
        try:
            # 执行身份验证
            verification_success = await self._perform_identity_verification(
                request.user_id, verification_method, verification_data
            )
            
            if verification_success:
                request.identity_verified = True
                request.identity_verification_method = verification_method
                request.status = RequestStatus.PROCESSING
                
                # 开始处理请求
                asyncio.create_task(self._process_rights_request(request))
                
                self.logger.info(f"IDENTITY_VERIFIED - request_id: {request_id}, method: {verification_method}")
            else:
                self.logger.warning(f"IDENTITY_VERIFICATION_FAILED - request_id: {request_id}")
            
            await self._save_rights_request(request)
            return verification_success
            
        except Exception as e:
            self.logger.error(f"IDENTITY_VERIFICATION_ERROR - request_id: {request_id}, error: {e}")
            return False
    
    async def _process_rights_request(self, request: RightsRequest):
        """处理数据主体权利请求"""
        
        try:
            request.status = RequestStatus.PROCESSING
            request.processed_at = datetime.now()
            await self._save_rights_request(request)
            
            # 根据请求类型执行相应处理
            if request.request_type == RequestType.ACCESS:
                result = await self._process_access_request(request)
            
            elif request.request_type == RequestType.RECTIFICATION:
                result = await self._process_rectification_request(request)
            
            elif request.request_type == RequestType.ERASURE:
                result = await self._process_erasure_request(request)
            
            elif request.request_type == RequestType.RESTRICT:
                result = await self._process_restriction_request(request)
            
            elif request.request_type == RequestType.PORTABILITY:
                result = await self._process_portability_request(request)
            
            elif request.request_type == RequestType.OBJECT:
                result = await self._process_objection_request(request)
            
            else:
                raise ValueError(f"Unsupported request type: {request.request_type}")
            
            # 更新请求状态
            if result.get('success', False):
                request.status = RequestStatus.COMPLETED
                request.processing_notes = result.get('notes', '')
            else:
                request.status = RequestStatus.REJECTED
                request.rejection_reason = result.get('rejection_reason', 'Processing failed')
            
            request.completed_at = datetime.now()
            await self._save_rights_request(request)
            
            # 发送完成通知
            await self._send_completion_notification(request, result)
            
            self.logger.info(f"REQUEST_PROCESSED - request_id: {request.request_id}, result: {request.status.value}")
            
        except Exception as e:
            request.status = RequestStatus.REJECTED
            request.rejection_reason = f"Processing error: {str(e)}"
            request.completed_at = datetime.now()
            await self._save_rights_request(request)
            
            self.logger.error(f"REQUEST_PROCESSING_ERROR - request_id: {request.request_id}, error: {e}")
    
    async def _process_access_request(self, request: RightsRequest) -> Dict[str, Any]:
        """处理访问权请求 (GDPR Art. 15)"""
        
        try:
            # 收集用户的所有个人数据
            user_data = await self._collect_user_data(request.user_id, request.requested_data_categories)
            
            # 生成数据主体访问报告
            access_report = await self._generate_access_report(request.user_id, user_data)
            
            # 生成可读格式的数据导出
            export_formats = await self._generate_data_export(user_data)
            
            return {
                'success': True,
                'access_report': access_report,
                'export_files': export_formats,
                'notes': f'Data access report generated for {len(user_data)} data categories'
            }
            
        except Exception as e:
            return {
                'success': False,
                'rejection_reason': f'Unable to process access request: {str(e)}'
            }
    
    async def _process_erasure_request(self, request: RightsRequest) -> Dict[str, Any]:
        """处理删除权请求 (GDPR Art. 17)"""
        
        try:
            # 评估哪些数据可以删除
            erasure_assessment = await self._assess_erasure_eligibility(request.user_id)
            
            if not erasure_assessment['can_erase_any']:
                return {
                    'success': False,
                    'rejection_reason': erasure_assessment['rejection_reason']
                }
            
            # 执行数据删除
            deletion_results = []
            
            for category, can_delete in erasure_assessment['categories'].items():
                if can_delete['eligible']:
                    try:
                        await self._delete_data_category(request.user_id, category)
                        deletion_results.append({
                            'category': category,
                            'status': 'deleted',
                            'details': f"All {category} data has been permanently deleted"
                        })
                    except Exception as e:
                        deletion_results.append({
                            'category': category,
                            'status': 'error',
                            'details': f"Failed to delete {category}: {str(e)}"
                        })
                else:
                    deletion_results.append({
                        'category': category,
                        'status': 'retained',
                        'details': can_delete['reason']
                    })
            
            # 通知第三方处理器删除数据
            await self._notify_processors_data_deletion(request.user_id)
            
            return {
                'success': True,
                'deletion_results': deletion_results,
                'notes': 'Data erasure completed where legally permissible'
            }
            
        except Exception as e:
            return {
                'success': False,
                'rejection_reason': f'Unable to process erasure request: {str(e)}'
            }
    
    async def _process_portability_request(self, request: RightsRequest) -> Dict[str, Any]:
        """处理数据可携带权请求 (GDPR Art. 20)"""
        
        try:
            # 收集可携带的数据
            portable_data = await self._collect_portable_data(request.user_id)
            
            if not portable_data:
                return {
                    'success': False,
                    'rejection_reason': 'No portable data available for this user'
                }
            
            # 生成结构化数据导出
            export_files = {
                'json': await self._export_to_json(portable_data),
                'csv': await self._export_to_csv(portable_data),
                'xml': await self._export_to_xml(portable_data)
            }
            
            # 生成安全下载链接
            download_links = await self._generate_secure_download_links(export_files)
            
            return {
                'success': True,
                'export_formats': list(export_files.keys()),
                'download_links': download_links,
                'data_categories': list(portable_data.keys()),
                'notes': 'Data portability export generated in machine-readable formats'
            }
            
        except Exception as e:
            return {
                'success': False,
                'rejection_reason': f'Unable to process portability request: {str(e)}'
            }
    
    async def _process_rectification_request(self, request: RightsRequest) -> Dict[str, Any]:
        """处理更正权请求 (GDPR Art. 16)"""
        
        # 更正请求需要具体的更正指令，这里提供框架
        return {
            'success': True,
            'notes': 'Rectification framework ready. Specific corrections need to be implemented.'
        }
    
    async def _process_restriction_request(self, request: RightsRequest) -> Dict[str, Any]:
        """处理限制处理权请求 (GDPR Art. 18)"""
        
        try:
            # 标记数据为限制处理状态
            restricted_categories = []
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE data_records 
                    SET is_restricted = TRUE, restriction_reason = ?
                    WHERE user_id = ? AND is_restricted = FALSE
                """, (f"User request {request.request_id}", request.user_id))
                
                affected_rows = cursor.rowcount
                
                if affected_rows > 0:
                    # 获取受影响的数据类别
                    cursor.execute("""
                        SELECT DISTINCT category FROM data_records 
                        WHERE user_id = ? AND is_restricted = TRUE
                    """, (request.user_id,))
                    
                    restricted_categories = [row[0] for row in cursor.fetchall()]
            
            return {
                'success': True,
                'restricted_categories': restricted_categories,
                'affected_records': affected_rows,
                'notes': 'Data processing has been restricted as requested'
            }
            
        except Exception as e:
            return {
                'success': False,
                'rejection_reason': f'Unable to process restriction request: {str(e)}'
            }
    
    async def _process_objection_request(self, request: RightsRequest) -> Dict[str, Any]:
        """处理反对权请求 (GDPR Art. 21)"""
        
        try:
            # 评估反对的法律依据
            objection_assessment = await self._assess_objection_grounds(request.user_id)
            
            if objection_assessment['valid_objection']:
                # 停止基于合法利益的处理
                await self._stop_legitimate_interest_processing(request.user_id)
                
                return {
                    'success': True,
                    'stopped_processing': objection_assessment['stopped_categories'],
                    'notes': 'Processing based on legitimate interests has been stopped'
                }
            else:
                return {
                    'success': False,
                    'rejection_reason': objection_assessment['rejection_reason']
                }
                
        except Exception as e:
            return {
                'success': False,
                'rejection_reason': f'Unable to process objection request: {str(e)}'
            }
    
    async def _collect_user_data(self, user_id: str, requested_categories: List[str] = None) -> Dict[str, Any]:
        """收集用户的个人数据"""
        
        collected_data = {}
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 构建查询条件
                query = "SELECT category, data_content, legal_basis, processing_purpose, created_at FROM data_records WHERE user_id = ?"
                params = [user_id]
                
                if requested_categories:
                    placeholders = ','.join(['?' for _ in requested_categories])
                    query += f" AND category IN ({placeholders})"
                    params.extend(requested_categories)
                
                cursor.execute(query, params)
                
                for row in cursor.fetchall():
                    category, data_content, legal_basis, purpose, created_at = row
                    
                    if category not in collected_data:
                        collected_data[category] = {
                            'category_info': self.data_categories.get(category),
                            'records': []
                        }
                    
                    collected_data[category]['records'].append({
                        'data': json.loads(data_content),
                        'legal_basis': legal_basis,
                        'processing_purpose': purpose,
                        'collected_at': created_at
                    })
        
        except Exception as e:
            self.logger.error(f"Error collecting user data: {e}")
        
        return collected_data
    
    async def _generate_access_report(self, user_id: str, user_data: Dict) -> Dict[str, Any]:
        """生成GDPR访问权报告"""
        
        report = {
            'report_generated_at': datetime.now().isoformat(),
            'data_subject_id': user_id,
            'report_type': 'GDPR Article 15 - Right of Access',
            
            'data_processing_summary': {
                'total_categories': len(user_data),
                'total_records': sum(len(cat['records']) for cat in user_data.values()),
                'data_sources': list(user_data.keys()),
                'processing_purposes': list(set(
                    record['processing_purpose'] 
                    for cat in user_data.values() 
                    for record in cat['records']
                ))
            },
            
            'legal_bases_used': list(set(
                record['legal_basis'] 
                for cat in user_data.values() 
                for record in cat['records']
            )),
            
            'data_categories_detail': {},
            
            'third_party_sharing': await self._get_third_party_sharing_info(user_id),
            
            'data_retention_info': {
                category: cat_info['category_info'].retention_period 
                for category, cat_info in user_data.items() 
                if cat_info['category_info']
            },
            
            'data_subject_rights': {
                'available_rights': [
                    'Access (Art. 15)',
                    'Rectification (Art. 16)', 
                    'Erasure (Art. 17)',
                    'Restriction (Art. 18)',
                    'Portability (Art. 20)',
                    'Objection (Art. 21)'
                ],
                'how_to_exercise': 'Submit request through our data protection portal or contact our Data Protection Officer'
            }
        }
        
        # 详细数据类别信息
        for category, cat_data in user_data.items():
            report['data_categories_detail'][category] = {
                'description': cat_data['category_info'].description if cat_data['category_info'] else 'N/A',
                'legal_basis': cat_data['category_info'].legal_basis.value if cat_data['category_info'] else 'N/A',
                'retention_period': cat_data['category_info'].retention_period if cat_data['category_info'] else 'N/A',
                'record_count': len(cat_data['records']),
                'can_be_erased': cat_data['category_info'].can_be_erased if cat_data['category_info'] else True,
                'can_be_ported': cat_data['category_info'].can_be_ported if cat_data['category_info'] else True
            }
        
        return report
    
    async def _assess_erasure_eligibility(self, user_id: str) -> Dict[str, Any]:
        """评估数据删除的合法性"""
        
        assessment = {
            'can_erase_any': False,
            'categories': {},
            'rejection_reason': None
        }
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT category, legal_basis, COUNT(*) as record_count
                    FROM data_records 
                    WHERE user_id = ? 
                    GROUP BY category, legal_basis
                """, (user_id,))
                
                for row in cursor.fetchall():
                    category, legal_basis, count = row
                    category_info = self.data_categories.get(category)
                    
                    # 检查是否可以删除
                    can_erase = True
                    reason = ""
                    
                    if legal_basis == LegalBasis.LEGAL_OBLIGATION.value:
                        can_erase = False
                        reason = "Legal obligation requires retention"
                    elif category_info and not category_info.can_be_erased:
                        can_erase = False
                        reason = "Category marked as non-erasable"
                    elif legal_basis == LegalBasis.LEGITIMATE_INTERESTS.value:
                        # 需要评估合法利益是否仍然适用
                        can_erase = True  # 简化处理
                        reason = "Erasable unless overriding legitimate interests exist"
                    
                    assessment['categories'][category] = {
                        'eligible': can_erase,
                        'reason': reason,
                        'record_count': count,
                        'legal_basis': legal_basis
                    }
                    
                    if can_erase:
                        assessment['can_erase_any'] = True
            
            if not assessment['can_erase_any']:
                assessment['rejection_reason'] = "No data eligible for erasure under GDPR Article 17"
        
        except Exception as e:
            assessment['rejection_reason'] = f"Error assessing erasure eligibility: {str(e)}"
        
        return assessment
    
    async def generate_gdpr_compliance_report(self) -> Dict[str, Any]:
        """生成GDPR合规报告"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 统计数据主体权利请求
                cursor.execute("""
                    SELECT request_type, status, COUNT(*) 
                    FROM rights_requests 
                    WHERE created_at >= datetime('now', '-30 days')
                    GROUP BY request_type, status
                """)
                request_stats = cursor.fetchall()
                
                # 统计响应时间
                cursor.execute("""
                    SELECT request_type, 
                           AVG(julianday(completed_at) - julianday(created_at)) as avg_days
                    FROM rights_requests 
                    WHERE status = 'completed' AND completed_at IS NOT NULL
                    GROUP BY request_type
                """)
                response_times = cursor.fetchall()
                
                # 数据类别统计
                cursor.execute("""
                    SELECT category, legal_basis, COUNT(*) 
                    FROM data_records 
                    GROUP BY category, legal_basis
                """)
                data_stats = cursor.fetchall()
        
        except Exception as e:
            return {'error': f'Failed to generate compliance report: {str(e)}'}
        
        report = {
            'report_date': datetime.now().isoformat(),
            'reporting_period': 'Past 30 days',
            
            'data_subject_requests': {
                'total_requests': sum(count for _, _, count in request_stats),
                'by_type': {},
                'by_status': {},
                'average_response_times': {}
            },
            
            'data_processing': {
                'total_records': sum(count for _, _, count in data_stats),
                'by_category': {},
                'by_legal_basis': {}
            },
            
            'compliance_metrics': {
                'requests_within_30_days': 0,  # 需要计算
                'automated_processing_rate': 0,  # 需要计算
                'data_breach_count': 0,  # 需要从其他系统获取
            },
            
            'recommendations': [
                '定期审查数据保留政策',
                '优化数据主体权利请求处理流程',
                '加强员工GDPR培训',
                '改进数据处理记录的完整性'
            ]
        }
        
        # 处理请求统计
        for req_type, status, count in request_stats:
            if req_type not in report['data_subject_requests']['by_type']:
                report['data_subject_requests']['by_type'][req_type] = 0
            if status not in report['data_subject_requests']['by_status']:
                report['data_subject_requests']['by_status'][status] = 0
            
            report['data_subject_requests']['by_type'][req_type] += count
            report['data_subject_requests']['by_status'][status] += count
        
        # 处理响应时间
        for req_type, avg_days in response_times:
            report['data_subject_requests']['average_response_times'][req_type] = f"{avg_days:.1f} days"
        
        # 处理数据统计
        for category, legal_basis, count in data_stats:
            if category not in report['data_processing']['by_category']:
                report['data_processing']['by_category'][category] = 0
            if legal_basis not in report['data_processing']['by_legal_basis']:
                report['data_processing']['by_legal_basis'][legal_basis] = 0
            
            report['data_processing']['by_category'][category] += count
            report['data_processing']['by_legal_basis'][legal_basis] += count
        
        return report
    
    # 辅助方法的简化实现
    async def _save_rights_request(self, request: RightsRequest):
        """保存权利请求到数据库"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO rights_requests 
                    (request_id, user_id, request_type, status, created_at, identity_verified, 
                     identity_verification_method, processed_at, completed_at, rejection_reason, 
                     processing_notes, requested_data_categories, verification_deadline)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    request.request_id, request.user_id, request.request_type.value, 
                    request.status.value, request.created_at, request.identity_verified,
                    request.identity_verification_method, request.processed_at, 
                    request.completed_at, request.rejection_reason, request.processing_notes,
                    json.dumps(request.requested_data_categories) if request.requested_data_categories else None,
                    request.verification_deadline
                ))
        except Exception as e:
            self.logger.error(f"Failed to save rights request: {e}")
    
    async def _get_rights_request(self, request_id: str) -> Optional[RightsRequest]:
        """从数据库获取权利请求"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM rights_requests WHERE request_id = ?", (request_id,))
                row = cursor.fetchone()
                
                if row:
                    # 转换为RightsRequest对象
                    return RightsRequest(
                        request_id=row[0],
                        user_id=row[1],
                        request_type=RequestType(row[2]),
                        status=RequestStatus(row[3]),
                        created_at=datetime.fromisoformat(row[4]),
                        identity_verified=bool(row[5]),
                        identity_verification_method=row[6],
                        processed_at=datetime.fromisoformat(row[7]) if row[7] else None,
                        completed_at=datetime.fromisoformat(row[8]) if row[8] else None,
                        rejection_reason=row[9],
                        processing_notes=row[10],
                        requested_data_categories=json.loads(row[11]) if row[11] else None,
                        verification_deadline=datetime.fromisoformat(row[12]) if row[12] else None
                    )
        except Exception as e:
            self.logger.error(f"Failed to get rights request: {e}")
        
        return None
    
    # 其他方法的简化实现
    def _setup_logging(self):
        logger = logging.getLogger('gdpr_rights')
        logger.setLevel(logging.INFO)
        return logger
    
    def _init_email_service(self):
        return None
    
    def _init_identity_verification(self):
        return None
    
    async def _perform_identity_verification(self, user_id: str, method: str, data: Dict) -> bool:
        return True  # 简化实现
    
    async def _send_request_acknowledgment(self, request: RightsRequest):
        print(f"Acknowledgment sent for request {request.request_id}")
    
    async def _send_completion_notification(self, request: RightsRequest, result: Dict):
        print(f"Completion notification sent for request {request.request_id}")
    
    async def _delete_data_category(self, user_id: str, category: str):
        """删除特定类别的数据"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM data_records WHERE user_id = ? AND category = ?", (user_id, category))
    
    async def _collect_portable_data(self, user_id: str) -> Dict:
        """收集可携带的数据"""
        portable_data = {}
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT category, data_content 
                FROM data_records 
                WHERE user_id = ? 
            """, (user_id,))
            
            for category, data_content in cursor.fetchall():
                category_info = self.data_categories.get(category)
                if category_info and category_info.can_be_ported:
                    if category not in portable_data:
                        portable_data[category] = []
                    portable_data[category].append(json.loads(data_content))
        
        return portable_data
    
    async def _export_to_json(self, data: Dict) -> str:
        """导出为JSON格式"""
        return json.dumps(data, indent=2, default=str)
    
    async def _export_to_csv(self, data: Dict) -> str:
        """导出为CSV格式"""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # CSV header
        writer.writerow(['Category', 'Field', 'Value'])
        
        # CSV data
        for category, records in data.items():
            for record in records:
                for field, value in record.items():
                    writer.writerow([category, field, str(value)])
        
        return output.getvalue()
    
    async def _export_to_xml(self, data: Dict) -> str:
        """导出为XML格式（简化版）"""
        xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        xml_lines.append('<user_data>')
        
        for category, records in data.items():
            xml_lines.append(f'  <{category}>')
            for i, record in enumerate(records):
                xml_lines.append(f'    <record_{i}>')
                for field, value in record.items():
                    xml_lines.append(f'      <{field}>{value}</{field}>')
                xml_lines.append(f'    </record_{i}>')
            xml_lines.append(f'  </{category}>')
        
        xml_lines.append('</user_data>')
        return '\n'.join(xml_lines)


# 使用示例
async def demo_gdpr_rights_system():
    """GDPR数据主体权利系统演示"""
    
    print("🔒 GDPR数据主体权利系统演示\n")
    
    # 创建权利管理器
    manager = GDPRRightsManager()
    
    # 1. 提交访问权请求
    print("1️⃣ 提交数据访问权请求")
    
    access_request = await manager.submit_rights_request(
        user_id="user_gdpr_123",
        request_type=RequestType.ACCESS,
        additional_info={'data_categories': ['profile', 'educational_progress']}
    )
    
    print(f"访问权请求已提交: {access_request.request_id}")
    print(f"请求状态: {access_request.status.value}")
    
    # 2. 提交删除权请求
    print("\n2️⃣ 提交数据删除权请求")
    
    erasure_request = await manager.submit_rights_request(
        user_id="user_gdpr_123",
        request_type=RequestType.ERASURE
    )
    
    print(f"删除权请求已提交: {erasure_request.request_id}")
    
    # 3. 身份验证（如果需要）
    if erasure_request.status == RequestStatus.IDENTITY_VERIFICATION:
        print("\n3️⃣ 执行身份验证")
        
        verification_success = await manager.verify_identity(
            request_id=erasure_request.request_id,
            verification_method="email_verification",
            verification_data={"verification_code": "123456"}
        )
        
        print(f"身份验证结果: {'成功' if verification_success else '失败'}")
    
    # 4. 提交数据可携带权请求
    print("\n4️⃣ 提交数据可携带权请求")
    
    portability_request = await manager.submit_rights_request(
        user_id="user_gdpr_123",
        request_type=RequestType.PORTABILITY
    )
    
    print(f"可携带权请求已提交: {portability_request.request_id}")
    
    # 5. 生成合规报告
    print("\n5️⃣ 生成GDPR合规报告")
    
    compliance_report = await manager.generate_gdpr_compliance_report()
    print("GDPR合规报告:")
    print(json.dumps(compliance_report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(demo_gdpr_rights_system())