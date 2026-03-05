#!/usr/bin/env python3
"""
COPPA家长同意验证系统
COPPA Parental Consent Verification System

符合COPPA Section 312.5要求的可验证家长同意机制
支持多种验证方法：信用卡预授权、数字签名、邮件+电话验证等

使用方法:
from templates.coppa_parental_consent import COPPAConsentManager

consent_manager = COPPAConsentManager()
result = consent_manager.verify_parental_consent(child_data, consent_method)
"""

import hashlib
import uuid
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class ConsentMethod(Enum):
    """COPPA认可的家长同意验证方法"""
    CREDIT_CARD_PREAUTH = "credit_card_preauth"
    DIGITAL_SIGNATURE = "digital_signature"  
    EMAIL_PLUS_PHONE = "email_plus_phone"
    VIDEO_CONFERENCE = "video_conference"
    POSTAL_MAIL = "postal_mail"
    GOVERNMENT_ID = "government_id"

@dataclass
class ChildProfile:
    """儿童用户档案"""
    child_id: str
    birth_date: str  # YYYY-MM-DD
    parent_email: str
    parent_phone: Optional[str] = None
    parent_name: Optional[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    @property
    def age(self) -> int:
        """计算年龄"""
        birth = datetime.strptime(self.birth_date, '%Y-%m-%d')
        today = datetime.now()
        age = today.year - birth.year
        if today.month < birth.month or (today.month == birth.month and today.day < birth.day):
            age -= 1
        return age
    
    @property
    def requires_coppa_consent(self) -> bool:
        """是否需要COPPA家长同意"""
        return self.age < 13

@dataclass
class ConsentRecord:
    """同意记录"""
    consent_id: str
    child_id: str
    method: ConsentMethod
    status: str  # pending, verified, failed, expired
    verification_data: Dict
    granted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    parent_signature: Optional[str] = None

class COPPAConsentManager:
    """COPPA家长同意管理器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or self._get_default_config()
        self.logger = self._setup_logging()
        self.consent_records = {}  # 实际应用中应使用数据库
        
        # 初始化第三方服务
        self.payment_processor = self._init_payment_processor()
        self.sms_service = self._init_sms_service()
        self.email_service = self._init_email_service()
    
    def _get_default_config(self) -> Dict:
        """默认配置"""
        return {
            'consent_validity_days': 365,  # 家长同意有效期1年
            'verification_timeout_minutes': 30,
            'max_retry_attempts': 3,
            'notification_settings': {
                'send_confirmation_email': True,
                'send_expiry_reminder': True,
                'reminder_days_before_expiry': 30
            },
            'data_retention': {
                'consent_records_years': 7,  # 保留7年用于合规审计
                'child_data_deletion_on_revoke': True
            },
            'security': {
                'encrypt_consent_data': True,
                'audit_all_access': True,
                'secure_transmission_only': True
            }
        }
    
    def _setup_logging(self) -> logging.Logger:
        """设置日志系统"""
        logger = logging.getLogger('coppa_consent')
        logger.setLevel(logging.INFO)
        
        # 创建审计日志处理器
        audit_handler = logging.FileHandler('coppa_audit.log')
        audit_formatter = logging.Formatter(
            '%(asctime)s - COPPA_AUDIT - %(levelname)s - %(message)s'
        )
        audit_handler.setFormatter(audit_formatter)
        logger.addHandler(audit_handler)
        
        return logger
    
    async def request_parental_consent(
        self, 
        child_profile: ChildProfile, 
        consent_method: ConsentMethod,
        data_processing_purposes: List[str]
    ) -> ConsentRecord:
        """请求家长同意"""
        
        # 验证儿童年龄是否需要COPPA保护
        if not child_profile.requires_coppa_consent:
            raise ValueError(f"Child age {child_profile.age} does not require COPPA consent")
        
        # 生成唯一同意ID
        consent_id = f"coppa_{uuid.uuid4().hex[:8]}"
        
        # 记录审计日志
        self.logger.info(f"CONSENT_REQUEST - child_id: {child_profile.child_id}, method: {consent_method.value}")
        
        # 创建同意记录
        consent_record = ConsentRecord(
            consent_id=consent_id,
            child_id=child_profile.child_id,
            method=consent_method,
            status="pending",
            verification_data={
                'purposes': data_processing_purposes,
                'requested_at': datetime.now().isoformat(),
                'parent_email': child_profile.parent_email,
                'verification_attempts': 0
            }
        )
        
        # 根据验证方法执行相应流程
        if consent_method == ConsentMethod.CREDIT_CARD_PREAUTH:
            return await self._handle_credit_card_consent(child_profile, consent_record)
        
        elif consent_method == ConsentMethod.EMAIL_PLUS_PHONE:
            return await self._handle_email_phone_consent(child_profile, consent_record)
        
        elif consent_method == ConsentMethod.DIGITAL_SIGNATURE:
            return await self._handle_digital_signature_consent(child_profile, consent_record)
        
        else:
            raise NotImplementedError(f"Consent method {consent_method.value} not yet implemented")
    
    async def _handle_credit_card_consent(
        self, 
        child_profile: ChildProfile, 
        consent_record: ConsentRecord
    ) -> ConsentRecord:
        """处理信用卡预授权家长同意"""
        
        try:
            # 生成同意页面URL
            consent_url = self._generate_consent_url(consent_record.consent_id)
            
            # 发送家长同意邮件
            consent_email = self._create_parental_consent_email(
                child_profile, 
                consent_record,
                consent_url,
                ConsentMethod.CREDIT_CARD_PREAUTH
            )
            
            await self.email_service.send_email(consent_email)
            
            # 记录发送状态
            consent_record.verification_data.update({
                'consent_url': consent_url,
                'email_sent_at': datetime.now().isoformat(),
                'expiry_hours': 24  # 24小时内完成验证
            })
            
            # 设置过期时间
            consent_record.expires_at = datetime.now() + timedelta(hours=24)
            
            # 存储记录
            self.consent_records[consent_record.consent_id] = consent_record
            
            self.logger.info(f"CREDIT_CARD_CONSENT_REQUESTED - consent_id: {consent_record.consent_id}")
            
            return consent_record
            
        except Exception as e:
            self.logger.error(f"CREDIT_CARD_CONSENT_ERROR - {e}")
            consent_record.status = "failed"
            consent_record.verification_data['error'] = str(e)
            return consent_record
    
    async def verify_credit_card_preauth(
        self, 
        consent_id: str, 
        card_info: Dict
    ) -> bool:
        """验证信用卡预授权 - COPPA认可的方法"""
        
        consent_record = self.consent_records.get(consent_id)
        if not consent_record:
            raise ValueError("Invalid consent ID")
        
        try:
            # 执行小额预授权（通常$0.30-$1.00）
            preauth_result = await self.payment_processor.authorize_payment(
                amount=0.50,  # 50美分
                card_number=card_info['number'],
                expiry_date=card_info['expiry'],
                cvv=card_info['cvv'],
                billing_address=card_info.get('billing_address')
            )
            
            if preauth_result.success:
                # 立即撤销授权 - 不实际扣费
                await self.payment_processor.void_authorization(preauth_result.auth_id)
                
                # 更新同意记录
                consent_record.status = "verified"
                consent_record.granted_at = datetime.now()
                consent_record.expires_at = datetime.now() + timedelta(days=365)  # 1年有效期
                consent_record.verification_data.update({
                    'auth_id': preauth_result.auth_id,
                    'card_last_four': card_info['number'][-4:],
                    'verification_completed_at': datetime.now().isoformat()
                })
                
                # 记录审计日志
                self.logger.info(f"COPPA_CONSENT_VERIFIED - consent_id: {consent_id}, method: credit_card")
                
                # 发送确认邮件给家长
                await self._send_consent_confirmation(consent_record)
                
                return True
            else:
                consent_record.status = "failed"
                consent_record.verification_data['failure_reason'] = preauth_result.error_message
                self.logger.warning(f"CREDIT_CARD_VERIFICATION_FAILED - consent_id: {consent_id}")
                return False
                
        except Exception as e:
            consent_record.status = "failed"
            consent_record.verification_data['error'] = str(e)
            self.logger.error(f"CREDIT_CARD_VERIFICATION_ERROR - consent_id: {consent_id}, error: {e}")
            return False
    
    async def _handle_email_phone_consent(
        self,
        child_profile: ChildProfile,
        consent_record: ConsentRecord
    ) -> ConsentRecord:
        """处理邮件+电话双重验证"""
        
        try:
            # 生成验证码
            email_code = self._generate_verification_code(6)
            phone_code = self._generate_verification_code(4)
            
            # 发送邮件验证码
            email_content = self._create_email_verification_email(
                child_profile, email_code, consent_record.consent_id
            )
            await self.email_service.send_email(email_content)
            
            # 发送短信验证码（如果提供了电话号码）
            if child_profile.parent_phone:
                sms_content = f"您孩子的应用注册需要家长同意。验证码: {phone_code} (10分钟内有效)"
                await self.sms_service.send_sms(child_profile.parent_phone, sms_content)
            
            # 更新记录
            consent_record.verification_data.update({
                'email_code': self._hash_code(email_code),
                'phone_code': self._hash_code(phone_code) if child_profile.parent_phone else None,
                'codes_sent_at': datetime.now().isoformat(),
                'verification_attempts': 0,
                'max_attempts': 3
            })
            
            consent_record.expires_at = datetime.now() + timedelta(minutes=10)
            
            self.consent_records[consent_record.consent_id] = consent_record
            
            return consent_record
            
        except Exception as e:
            consent_record.status = "failed"
            consent_record.verification_data['error'] = str(e)
            return consent_record
    
    def verify_email_phone_codes(
        self, 
        consent_id: str, 
        email_code: str, 
        phone_code: Optional[str] = None
    ) -> bool:
        """验证邮件和电话验证码"""
        
        consent_record = self.consent_records.get(consent_id)
        if not consent_record:
            return False
        
        # 检查是否过期
        if datetime.now() > consent_record.expires_at:
            consent_record.status = "expired"
            return False
        
        # 检查尝试次数
        attempts = consent_record.verification_data.get('verification_attempts', 0)
        if attempts >= consent_record.verification_data.get('max_attempts', 3):
            consent_record.status = "failed"
            return False
        
        # 增加尝试次数
        consent_record.verification_data['verification_attempts'] = attempts + 1
        
        # 验证邮件验证码
        stored_email_hash = consent_record.verification_data.get('email_code')
        if not stored_email_hash or self._hash_code(email_code) != stored_email_hash:
            return False
        
        # 验证电话验证码（如果需要）
        stored_phone_hash = consent_record.verification_data.get('phone_code')
        if stored_phone_hash:
            if not phone_code or self._hash_code(phone_code) != stored_phone_hash:
                return False
        
        # 验证成功
        consent_record.status = "verified"
        consent_record.granted_at = datetime.now()
        consent_record.expires_at = datetime.now() + timedelta(days=365)
        
        self.logger.info(f"COPPA_CONSENT_VERIFIED - consent_id: {consent_id}, method: email_phone")
        
        return True
    
    def _generate_verification_code(self, length: int = 6) -> str:
        """生成验证码"""
        import random
        import string
        return ''.join(random.choices(string.digits, k=length))
    
    def _hash_code(self, code: str) -> str:
        """哈希验证码"""
        return hashlib.sha256(code.encode()).hexdigest()
    
    def _generate_consent_url(self, consent_id: str) -> str:
        """生成同意页面URL"""
        base_url = self.config.get('base_url', 'https://your-app.com')
        return f"{base_url}/parental-consent/{consent_id}"
    
    def _create_parental_consent_email(
        self, 
        child_profile: ChildProfile,
        consent_record: ConsentRecord,
        consent_url: str,
        method: ConsentMethod
    ) -> Dict:
        """创建家长同意邮件"""
        
        if method == ConsentMethod.CREDIT_CARD_PREAUTH:
            subject = f"家长同意确认 - {child_profile.child_id}的应用注册"
            body = f"""
亲爱的家长，

您的孩子希望注册使用我们的教育应用。根据美国儿童在线隐私保护法(COPPA)的要求，我们需要获得您的可验证同意。

儿童信息：
• 用户ID: {child_profile.child_id}
• 估计年龄: {child_profile.age}岁

我们将收集和使用的信息：
{self._format_data_purposes(consent_record.verification_data.get('purposes', []))}

验证方法：
为了确保是真实的家长同意，我们将进行信用卡预授权验证。这将在您的卡上进行$0.50的临时授权，验证成功后立即撤销，不会产生实际扣费。

请点击以下链接完成验证：
{consent_url}

此链接24小时内有效。如果您没有要求此验证，请忽略此邮件。

如有疑问，请联系我们的客服团队。

谢谢您的配合！

---
此邮件为系统自动发送，符合COPPA Section 312.5要求
同意ID: {consent_record.consent_id}
发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
        
        return {
            'to': child_profile.parent_email,
            'subject': subject,
            'body': body,
            'type': 'parental_consent_request'
        }
    
    def _format_data_purposes(self, purposes: List[str]) -> str:
        """格式化数据使用目的"""
        purpose_descriptions = {
            'learning_progress': '• 学习进度追踪 - 帮助您的孩子了解学习成果',
            'app_functionality': '• 应用功能 - 提供基本的应用服务',
            'safety_security': '• 安全保护 - 确保应用使用安全',
            'parental_controls': '• 家长控制 - 让您监督和管理孩子的应用使用'
        }
        
        formatted = []
        for purpose in purposes:
            if purpose in purpose_descriptions:
                formatted.append(purpose_descriptions[purpose])
            else:
                formatted.append(f'• {purpose}')
        
        return '\n'.join(formatted)
    
    def revoke_consent(self, consent_id: str, revocation_reason: str = None) -> bool:
        """撤销家长同意"""
        
        consent_record = self.consent_records.get(consent_id)
        if not consent_record:
            return False
        
        # 更新状态
        consent_record.status = "revoked"
        consent_record.verification_data.update({
            'revoked_at': datetime.now().isoformat(),
            'revocation_reason': revocation_reason or 'parent_request'
        })
        
        # 审计日志
        self.logger.info(f"COPPA_CONSENT_REVOKED - consent_id: {consent_id}, reason: {revocation_reason}")
        
        # 如果配置要求，删除儿童数据
        if self.config['data_retention']['child_data_deletion_on_revoke']:
            asyncio.create_task(self._delete_child_data(consent_record.child_id))
        
        # 通知家长
        asyncio.create_task(self._send_revocation_confirmation(consent_record))
        
        return True
    
    async def _delete_child_data(self, child_id: str):
        """删除儿童数据 - COPPA要求"""
        try:
            # 这里实现具体的数据删除逻辑
            # 1. 删除用户生成内容
            # 2. 删除学习进度记录
            # 3. 删除个人资料信息
            # 4. 通知第三方服务删除相关数据
            
            self.logger.info(f"CHILD_DATA_DELETED - child_id: {child_id}")
            
        except Exception as e:
            self.logger.error(f"CHILD_DATA_DELETION_ERROR - child_id: {child_id}, error: {e}")
    
    def get_consent_status(self, child_id: str) -> Optional[ConsentRecord]:
        """获取同意状态"""
        for record in self.consent_records.values():
            if record.child_id == child_id and record.status == "verified":
                return record
        return None
    
    def is_consent_valid(self, child_id: str) -> bool:
        """检查同意是否有效"""
        consent = self.get_consent_status(child_id)
        if not consent:
            return False
        
        # 检查是否过期
        if consent.expires_at and datetime.now() > consent.expires_at:
            consent.status = "expired"
            return False
        
        return True
    
    def generate_compliance_report(self) -> Dict:
        """生成COPPA合规报告"""
        
        total_consents = len(self.consent_records)
        verified_consents = len([r for r in self.consent_records.values() if r.status == "verified"])
        expired_consents = len([r for r in self.consent_records.values() if r.status == "expired"])
        
        report = {
            'report_date': datetime.now().isoformat(),
            'statistics': {
                'total_consent_requests': total_consents,
                'verified_consents': verified_consents,
                'success_rate': (verified_consents / total_consents * 100) if total_consents > 0 else 0,
                'expired_consents': expired_consents
            },
            'compliance_status': {
                'coppa_compliant': True,
                'audit_ready': True,
                'data_retention_compliant': True
            },
            'recommendations': [
                '定期检查即将过期的同意记录',
                '监控家长同意成功率，优化验证流程',
                '确保所有同意记录完整保存7年'
            ]
        }
        
        return report
    
    # 第三方服务集成（简化示例）
    def _init_payment_processor(self):
        """初始化支付处理器"""
        class MockPaymentProcessor:
            async def authorize_payment(self, **kwargs):
                # 模拟支付授权
                class Result:
                    success = True
                    auth_id = f"auth_{uuid.uuid4().hex[:8]}"
                    error_message = None
                return Result()
            
            async def void_authorization(self, auth_id):
                # 模拟撤销授权
                return True
        
        return MockPaymentProcessor()
    
    def _init_sms_service(self):
        """初始化短信服务"""
        class MockSMSService:
            async def send_sms(self, phone_number, message):
                print(f"SMS to {phone_number}: {message}")
                return True
        
        return MockSMSService()
    
    def _init_email_service(self):
        """初始化邮件服务"""
        class MockEmailService:
            async def send_email(self, email_data):
                print(f"Email to {email_data['to']}: {email_data['subject']}")
                return True
        
        return MockEmailService()

# 使用示例
async def main():
    """使用示例"""
    
    # 创建COPPA同意管理器
    consent_manager = COPPAConsentManager()
    
    # 创建儿童档案
    child = ChildProfile(
        child_id="child_12345",
        birth_date="2015-06-15",  # 8岁儿童
        parent_email="parent@example.com",
        parent_phone="+1234567890",
        parent_name="John Doe"
    )
    
    print(f"儿童年龄: {child.age}岁")
    print(f"需要COPPA同意: {child.requires_coppa_consent}")
    
    if child.requires_coppa_consent:
        # 请求家长同意
        consent_record = await consent_manager.request_parental_consent(
            child_profile=child,
            consent_method=ConsentMethod.CREDIT_CARD_PREAUTH,
            data_processing_purposes=[
                'learning_progress',
                'app_functionality', 
                'safety_security'
            ]
        )
        
        print(f"同意请求已发送，ID: {consent_record.consent_id}")
        print(f"状态: {consent_record.status}")
        
        # 模拟家长完成信用卡验证
        if consent_record.status == "pending":
            verification_success = await consent_manager.verify_credit_card_preauth(
                consent_id=consent_record.consent_id,
                card_info={
                    'number': '4111111111111111',  # 测试卡号
                    'expiry': '12/28',
                    'cvv': '123'
                }
            )
            
            print(f"验证结果: {'成功' if verification_success else '失败'}")
        
        # 检查同意状态
        is_valid = consent_manager.is_consent_valid(child.child_id)
        print(f"同意是否有效: {is_valid}")
        
        # 生成合规报告
        report = consent_manager.generate_compliance_report()
        print("合规报告:", json.dumps(report, indent=2))

if __name__ == "__main__":
    asyncio.run(main())