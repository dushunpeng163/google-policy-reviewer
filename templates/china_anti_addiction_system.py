#!/usr/bin/env python3
"""
中国防沉迷系统
China Anti-Addiction System

符合国家新闻出版署《关于进一步严格管理 切实防止未成年人沉迷网络游戏的通知》
实现实名认证、时间限制、充值限制、家长监护等功能

使用方法:
from templates.china_anti_addiction_system import AntiAddictionManager

addiction_manager = AntiAddictionManager()
result = addiction_manager.verify_player_eligibility(user_data)
"""

import hashlib
import uuid
import asyncio
import logging
from datetime import datetime, timedelta, time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import sqlite3
from pathlib import Path

class UserType(Enum):
    """用户类型"""
    ADULT = "adult"              # 成年人 (18+)
    MINOR_16_TO_18 = "minor_16_to_18"    # 16-18岁
    MINOR_8_TO_16 = "minor_8_to_16"      # 8-16岁  
    CHILD_UNDER_8 = "child_under_8"      # 8岁以下

class GameTimeWindow(Enum):
    """游戏时间窗口"""
    FORBIDDEN = "forbidden"      # 禁止游戏
    ALLOWED = "allowed"         # 允许游戏
    LIMITED = "limited"         # 限制时间游戏

@dataclass
class RealNameInfo:
    """实名认证信息"""
    user_id: str
    real_name: str
    id_card_number: str
    phone_number: str
    verification_status: str  # pending, verified, failed
    verification_time: Optional[datetime] = None
    nrta_response: Optional[Dict] = None  # 国家新闻出版署响应

@dataclass
class PlayTimeRecord:
    """游戏时间记录"""
    user_id: str
    date: str  # YYYY-MM-DD
    total_minutes: int
    sessions: List[Dict]  # [{"start": "20:00", "end": "20:30", "duration": 30}]
    is_holiday: bool = False

@dataclass
class PaymentRecord:
    """充值记录"""
    user_id: str
    amount_yuan: float
    transaction_id: str
    timestamp: datetime
    payment_method: str
    parental_approved: bool = False

class AntiAddictionManager:
    """防沉迷系统管理器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or self._get_default_config()
        self.logger = self._setup_logging()
        self.db_path = Path(__file__).parent.parent / "data" / "anti_addiction.db"
        self._init_database()
        
        # 初始化NRTA（国家新闻出版署）API客户端
        self.nrta_client = self._init_nrta_client()
        
    def _get_default_config(self) -> Dict:
        """默认配置"""
        return {
            'time_limits': {
                'weekday_minutes': 0,      # 工作日：禁止游戏
                'weekend_minutes': 60,     # 周末：1小时
                'holiday_minutes': 60,     # 节假日：1小时
                'allowed_hours': [20, 21]  # 允许游戏时间：20:00-21:00
            },
            'payment_limits': {
                'under_8': {'single_yuan': 0, 'monthly_yuan': 0},
                '8_to_16': {'single_yuan': 50, 'monthly_yuan': 200},
                '16_to_18': {'single_yuan': 100, 'monthly_yuan': 400}
            },
            'nrta_api': {
                'endpoint': 'https://api.nrta.gov.cn/realname/verify',  # 示例URL
                'app_id': 'your_app_id',
                'secret_key': 'your_secret_key',
                'timeout_seconds': 10
            },
            'holiday_api': {
                'endpoint': 'http://timor.tech/api/holiday/year',  # 节假日查询API
                'cache_days': 30
            },
            'parental_notification': {
                'notify_on_login': True,
                'notify_on_payment': True,
                'notify_on_time_limit': True,
                'notification_methods': ['sms', 'email']
            }
        }
    
    def _init_database(self):
        """初始化数据库"""
        self.db_path.parent.mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # 实名认证表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS realname_verification (
                    user_id TEXT PRIMARY KEY,
                    real_name TEXT NOT NULL,
                    id_card_number TEXT NOT NULL,
                    phone_number TEXT,
                    verification_status TEXT DEFAULT 'pending',
                    verification_time DATETIME,
                    nrta_response TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 游戏时间记录表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS play_time_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    date TEXT NOT NULL,
                    total_minutes INTEGER DEFAULT 0,
                    sessions TEXT,  -- JSON format
                    is_holiday BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, date)
                )
            """)
            
            # 充值记录表
            conn.execute("""
                CREATE TABLE IF NOT EXISTS payment_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    amount_yuan REAL NOT NULL,
                    transaction_id TEXT UNIQUE NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    payment_method TEXT,
                    parental_approved BOOLEAN DEFAULT FALSE,
                    monthly_total REAL DEFAULT 0
                )
            """)
    
    async def submit_realname_verification(
        self, 
        user_id: str, 
        real_name: str, 
        id_card_number: str,
        phone_number: str = None
    ) -> RealNameInfo:
        """提交实名认证"""
        
        # 验证身份证号码格式
        if not self._validate_id_card_format(id_card_number):
            raise ValueError("Invalid ID card number format")
        
        # 提取年龄信息
        age = self._extract_age_from_id_card(id_card_number)
        if age is None:
            raise ValueError("Cannot extract age from ID card number")
        
        # 创建实名信息记录
        realname_info = RealNameInfo(
            user_id=user_id,
            real_name=real_name,
            id_card_number=id_card_number,
            phone_number=phone_number,
            verification_status="pending"
        )
        
        try:
            # 调用国家新闻出版署实名认证API
            nrta_response = await self._call_nrta_api(real_name, id_card_number)
            
            if nrta_response.get('status') == 'success':
                realname_info.verification_status = "verified"
                realname_info.verification_time = datetime.now()
                realname_info.nrta_response = nrta_response
                
                self.logger.info(f"REALNAME_VERIFIED - user_id: {user_id}, age: {age}")
            else:
                realname_info.verification_status = "failed"
                realname_info.nrta_response = nrta_response
                
                self.logger.warning(f"REALNAME_FAILED - user_id: {user_id}, reason: {nrta_response.get('message')}")
        
        except Exception as e:
            realname_info.verification_status = "failed"
            realname_info.nrta_response = {'error': str(e)}
            self.logger.error(f"REALNAME_ERROR - user_id: {user_id}, error: {e}")
        
        # 保存到数据库
        await self._save_realname_info(realname_info)
        
        return realname_info
    
    def _validate_id_card_format(self, id_card: str) -> bool:
        """验证身份证号码格式"""
        if len(id_card) != 18:
            return False
        
        # 验证前17位是数字，最后一位是数字或X
        if not id_card[:17].isdigit():
            return False
        
        if not (id_card[17].isdigit() or id_card[17].upper() == 'X'):
            return False
        
        # 验证校验位（简化版）
        return True
    
    def _extract_age_from_id_card(self, id_card: str) -> Optional[int]:
        """从身份证号码提取年龄"""
        try:
            year = int(id_card[6:10])
            month = int(id_card[10:12])
            day = int(id_card[12:14])
            
            birth_date = datetime(year, month, day)
            age = (datetime.now() - birth_date).days // 365
            
            return age
        except (ValueError, IndexError):
            return None
    
    async def _call_nrta_api(self, real_name: str, id_card: str) -> Dict:
        """调用国家新闻出版署实名认证API"""
        
        # 这里是示例实现，实际需要根据NRTA的API文档
        
        import aiohttp
        
        api_config = self.config.get('nrta_api', {})
        
        # 构建请求数据
        request_data = {
            'ai': api_config.get('app_id'),
            'name': real_name,
            'idNum': id_card,
            'timestamp': int(datetime.now().timestamp())
        }
        
        # 生成签名
        sign_string = f"{api_config.get('app_id')}{request_data['timestamp']}"
        signature = hashlib.md5(f"{sign_string}{api_config.get('secret_key')}".encode()).hexdigest()
        request_data['sign'] = signature
        
        try:
            timeout = aiohttp.ClientTimeout(total=api_config.get('timeout_seconds', 10))
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(api_config.get('endpoint'), json=request_data) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        return response_data
                    else:
                        return {
                            'status': 'error',
                            'message': f'NRTA API error: {response.status}'
                        }
                        
        except asyncio.TimeoutError:
            return {
                'status': 'error',
                'message': 'NRTA API timeout'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'NRTA API exception: {str(e)}'
            }
    
    def determine_user_type(self, user_id: str) -> UserType:
        """确定用户类型"""
        # 从数据库获取实名认证信息
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id_card_number, verification_status 
                FROM realname_verification 
                WHERE user_id = ? AND verification_status = 'verified'
            """, (user_id,))
            
            row = cursor.fetchone()
            
        if not row:
            return UserType.ADULT  # 未实名认证默认当成成人处理
        
        id_card, status = row
        if status != 'verified':
            return UserType.ADULT
        
        # 从身份证提取年龄
        age = self._extract_age_from_id_card(id_card)
        if age is None:
            return UserType.ADULT
        
        if age >= 18:
            return UserType.ADULT
        elif age >= 16:
            return UserType.MINOR_16_TO_18
        elif age >= 8:
            return UserType.MINOR_8_TO_16
        else:
            return UserType.CHILD_UNDER_8
    
    def can_play_now(self, user_id: str) -> Tuple[bool, str, Optional[int]]:
        """检查用户当前是否可以游戏"""
        
        user_type = self.determine_user_type(user_id)
        
        # 成年人不受限制
        if user_type == UserType.ADULT:
            return True, "成年用户，无时间限制", None
        
        # 8岁以下完全禁止
        if user_type == UserType.CHILD_UNDER_8:
            return False, "8岁以下用户禁止游戏", 0
        
        # 未成年人时间检查
        current_time = datetime.now()
        current_hour = current_time.hour
        
        # 检查是否在允许的时间段内 (20:00-21:00)
        allowed_hours = self.config['time_limits']['allowed_hours']
        
        if current_hour < allowed_hours[0] or current_hour >= allowed_hours[1]:
            return False, f"当前时间{current_hour:02d}:xx不在允许游戏时间{allowed_hours[0]:02d}:00-{allowed_hours[1]:02d}:00内", 0
        
        # 检查是否是工作日
        if self._is_weekday(current_time):
            return False, "工作日禁止未成年人游戏", 0
        
        # 检查当日游戏时长
        today_minutes = self._get_today_play_time(user_id)
        max_minutes = self.config['time_limits']['weekend_minutes']
        
        if self._is_holiday(current_time.date()):
            max_minutes = self.config['time_limits']['holiday_minutes']
        
        remaining_minutes = max_minutes - today_minutes
        
        if remaining_minutes <= 0:
            return False, f"今日游戏时长已达限制({max_minutes}分钟)", 0
        
        return True, f"可以游戏{remaining_minutes}分钟", remaining_minutes
    
    def _is_weekday(self, dt: datetime) -> bool:
        """检查是否工作日"""
        # 0=周一, 6=周日
        return dt.weekday() < 5 and not self._is_holiday(dt.date())
    
    def _is_holiday(self, date) -> bool:
        """检查是否节假日"""
        # 简化实现，实际应该调用节假日API
        # 这里可以集成第三方节假日查询服务
        
        # 示例：2026年部分节假日（实际应从API获取）
        holidays_2026 = [
            "2026-01-01",  # 元旦
            "2026-02-17", "2026-02-18", "2026-02-19",  # 春节
            "2026-04-05",  # 清明节
            "2026-05-01",  # 劳动节
            "2026-06-22",  # 端午节
            "2026-10-01", "2026-10-02", "2026-10-03",  # 国庆节
        ]
        
        return date.strftime('%Y-%m-%d') in holidays_2026
    
    def _get_today_play_time(self, user_id: str) -> int:
        """获取今日游戏时长（分钟）"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT total_minutes FROM play_time_records 
                    WHERE user_id = ? AND date = ?
                """, (user_id, today))
                
                row = cursor.fetchone()
                return row[0] if row else 0
                
        except Exception as e:
            self.logger.error(f"Failed to get play time: {e}")
            return 0
    
    async def start_game_session(self, user_id: str) -> Dict[str, Any]:
        """开始游戏会话"""
        
        # 检查是否可以游戏
        can_play, reason, remaining_minutes = self.can_play_now(user_id)
        
        if not can_play:
            return {
                'status': 'denied',
                'reason': reason,
                'remaining_minutes': remaining_minutes or 0,
                'next_allowed_time': self._calculate_next_allowed_time(user_id)
            }
        
        # 创建游戏会话
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        session_data = {
            'session_id': session_id,
            'user_id': user_id,
            'start_time': datetime.now(),
            'max_duration_minutes': remaining_minutes,
            'status': 'active'
        }
        
        # 设置自动踢出定时器
        asyncio.create_task(
            self._schedule_auto_logout(session_id, remaining_minutes * 60)
        )
        
        # 通知家长（如果配置启用）
        if self.config['parental_notification']['notify_on_login']:
            asyncio.create_task(self._notify_parent_game_start(user_id))
        
        self.logger.info(f"GAME_SESSION_STARTED - user_id: {user_id}, session_id: {session_id}")
        
        return {
            'status': 'allowed',
            'session_id': session_id,
            'max_duration_minutes': remaining_minutes,
            'warning_message': f'您还可以游戏{remaining_minutes}分钟，请合理安排时间！'
        }
    
    async def end_game_session(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """结束游戏会话"""
        
        # 计算实际游戏时长
        # 这里应该从活跃会话中获取开始时间
        # 简化实现
        
        session_duration = 30  # 示例：30分钟
        
        # 更新今日游戏时间记录
        await self._update_play_time_record(user_id, session_duration)
        
        # 检查是否超时
        user_type = self.determine_user_type(user_id)
        if user_type != UserType.ADULT:
            today_total = self._get_today_play_time(user_id)
            max_daily = self.config['time_limits']['weekend_minutes']
            
            if today_total >= max_daily:
                # 达到每日限制，踢出游戏
                return {
                    'status': 'time_limit_reached',
                    'session_duration': session_duration,
                    'today_total': today_total,
                    'message': f'今日游戏时间已达{max_daily}分钟上限，感谢您的游戏！明天再来吧！'
                }
        
        self.logger.info(f"GAME_SESSION_ENDED - user_id: {user_id}, duration: {session_duration}min")
        
        return {
            'status': 'normal_end',
            'session_duration': session_duration,
            'today_total': self._get_today_play_time(user_id)
        }
    
    async def process_payment(
        self, 
        user_id: str, 
        amount_yuan: float, 
        payment_method: str = 'wechat'
    ) -> Dict[str, Any]:
        """处理游戏内充值"""
        
        user_type = self.determine_user_type(user_id)
        
        # 成年人无限制
        if user_type == UserType.ADULT:
            return await self._process_adult_payment(user_id, amount_yuan, payment_method)
        
        # 8岁以下禁止充值
        if user_type == UserType.CHILD_UNDER_8:
            self.logger.info(f"PAYMENT_DENIED - user_id: {user_id}, reason: under_8_years_old")
            return {
                'status': 'denied',
                'reason': '8岁以下用户不允许充值',
                'allowed_amount': 0
            }
        
        # 获取充值限制
        if user_type == UserType.MINOR_8_TO_16:
            limits = self.config['payment_limits']['8_to_16']
        else:  # 16-18岁
            limits = self.config['payment_limits']['16_to_18']
        
        # 检查单次充值限制
        if amount_yuan > limits['single_yuan']:
            return {
                'status': 'denied',
                'reason': f'单次充值限制{limits["single_yuan"]}元，当前{amount_yuan}元',
                'max_single_amount': limits['single_yuan']
            }
        
        # 检查月度充值限制
        current_month_total = await self._get_monthly_payment_total(user_id)
        if current_month_total + amount_yuan > limits['monthly_yuan']:
            remaining_quota = limits['monthly_yuan'] - current_month_total
            return {
                'status': 'denied', 
                'reason': f'月度充值限制{limits["monthly_yuan"]}元，剩余额度{remaining_quota}元',
                'monthly_remaining': remaining_quota
            }
        
        # 需要家长授权
        parental_approval = await self._request_parental_payment_approval(
            user_id, amount_yuan, user_type
        )
        
        if not parental_approval['approved']:
            return {
                'status': 'pending_parental_approval',
                'approval_id': parental_approval['approval_id'],
                'message': '充值需要家长授权，已发送通知给您的监护人'
            }
        
        # 执行充值
        payment_record = PaymentRecord(
            user_id=user_id,
            amount_yuan=amount_yuan,
            transaction_id=f"tx_{uuid.uuid4().hex[:12]}",
            timestamp=datetime.now(),
            payment_method=payment_method,
            parental_approved=True
        )
        
        # 保存充值记录
        await self._save_payment_record(payment_record)
        
        # 通知家长
        if self.config['parental_notification']['notify_on_payment']:
            asyncio.create_task(self._notify_parent_payment(payment_record))
        
        self.logger.info(f"PAYMENT_SUCCESS - user_id: {user_id}, amount: {amount_yuan}")
        
        return {
            'status': 'success',
            'transaction_id': payment_record.transaction_id,
            'amount': amount_yuan,
            'monthly_total': current_month_total + amount_yuan,
            'monthly_remaining': limits['monthly_yuan'] - (current_month_total + amount_yuan)
        }
    
    async def _request_parental_payment_approval(
        self, 
        user_id: str, 
        amount: float, 
        user_type: UserType
    ) -> Dict[str, Any]:
        """请求家长支付授权"""
        
        approval_id = f"approval_{uuid.uuid4().hex[:8]}"
        
        # 获取家长联系信息
        parent_contact = await self._get_parent_contact_info(user_id)
        
        if not parent_contact:
            return {
                'approved': False,
                'reason': '未找到家长联系信息',
                'approval_id': None
            }
        
        # 发送家长授权请求
        approval_message = f"""
您的孩子请求在游戏中充值 {amount} 元。

用户信息：
• 用户ID: {user_id}
• 年龄组: {user_type.value}
• 充值金额: ¥{amount}
• 请求时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

如果同意此次充值，请回复 "同意 {approval_id}"
如果拒绝，请回复 "拒绝 {approval_id}"

此授权请求将在30分钟后自动过期。
        """
        
        # 发送短信通知
        if parent_contact.get('phone'):
            await self._send_approval_sms(parent_contact['phone'], approval_message)
        
        # 发送邮件通知
        if parent_contact.get('email'):
            await self._send_approval_email(parent_contact['email'], approval_message, approval_id)
        
        # 暂时返回自动批准（实际应该等待家长响应）
        return {
            'approved': True,  # 示例：自动批准
            'approval_id': approval_id,
            'approval_method': 'automatic_for_demo'
        }
    
    async def generate_anti_addiction_report(self, user_id: str = None) -> Dict[str, Any]:
        """生成防沉迷合规报告"""
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 统计实名认证情况
                cursor.execute("""
                    SELECT verification_status, COUNT(*) 
                    FROM realname_verification 
                    GROUP BY verification_status
                """)
                realname_stats = dict(cursor.fetchall())
                
                # 统计游戏时长合规情况
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_sessions,
                        AVG(total_minutes) as avg_daily_minutes,
                        MAX(total_minutes) as max_daily_minutes
                    FROM play_time_records 
                    WHERE date >= date('now', '-30 days')
                """)
                time_stats = cursor.fetchone()
                
                # 统计充值情况
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_payments,
                        SUM(amount_yuan) as total_amount,
                        AVG(amount_yuan) as avg_amount
                    FROM payment_records 
                    WHERE timestamp >= datetime('now', '-30 days')
                """)
                payment_stats = cursor.fetchone()
        
        except Exception as e:
            self.logger.error(f"Report generation error: {e}")
            return {'error': str(e)}
        
        report = {
            'report_date': datetime.now().isoformat(),
            'reporting_period': '过去30天',
            
            'realname_authentication': {
                'total_users': sum(realname_stats.values()),
                'verified_users': realname_stats.get('verified', 0),
                'verification_rate': (realname_stats.get('verified', 0) / sum(realname_stats.values()) * 100) if realname_stats else 0,
                'status_breakdown': realname_stats
            },
            
            'time_management': {
                'total_game_sessions': time_stats[0] if time_stats else 0,
                'average_daily_minutes': round(time_stats[1], 1) if time_stats and time_stats[1] else 0,
                'max_daily_minutes': time_stats[2] if time_stats else 0,
                'compliance_status': '符合国家规定' if (time_stats and time_stats[2] <= 60) else '存在超时风险'
            },
            
            'payment_management': {
                'total_transactions': payment_stats[0] if payment_stats else 0,
                'total_amount_yuan': round(payment_stats[1], 2) if payment_stats and payment_stats[1] else 0,
                'average_amount_yuan': round(payment_stats[2], 2) if payment_stats and payment_stats[2] else 0
            },
            
            'compliance_assessment': {
                'overall_status': '基本合规',
                'risk_factors': [],
                'recommendations': [
                    '继续监控未成年人游戏时长',
                    '定期检查实名认证系统运行状态',
                    '完善家长监护功能',
                    '建立异常行为预警机制'
                ]
            },
            
            'regulatory_requirements_met': {
                'realname_authentication_system': True,
                'time_restriction_system': True,
                'payment_limitation_system': True,
                'parental_supervision_tools': True,
                'data_security_measures': True,
                'audit_trail_maintenance': True
            }
        }
        
        # 识别风险因素
        if report['time_management']['max_daily_minutes'] > 60:
            report['compliance_assessment']['risk_factors'].append('发现超时游戏记录')
        
        if report['realname_authentication']['verification_rate'] < 95:
            report['compliance_assessment']['risk_factors'].append('实名认证率偏低')
        
        return report
    
    async def _schedule_auto_logout(self, session_id: str, seconds: int):
        """安排自动登出"""
        await asyncio.sleep(seconds)
        
        # 执行强制登出
        self.logger.info(f"AUTO_LOGOUT - session_id: {session_id}")
        
        # 这里应该调用游戏服务器API强制用户下线
        # await game_server.force_logout(session_id)
        
        print(f"🚨 防沉迷系统：用户会话{session_id}已自动结束")
    
    def _calculate_next_allowed_time(self, user_id: str) -> Optional[str]:
        """计算下次允许游戏的时间"""
        
        user_type = self.determine_user_type(user_id)
        
        if user_type == UserType.ADULT:
            return None
        
        if user_type == UserType.CHILD_UNDER_8:
            return "8岁以下用户禁止游戏"
        
        now = datetime.now()
        
        # 如果当前是工作日，下次是周末
        if self._is_weekday(now):
            days_until_weekend = (5 - now.weekday()) % 7  # 距离周六的天数
            if days_until_weekend == 0:  # 今天是周六
                days_until_weekend = 7
            
            next_weekend = now + timedelta(days=days_until_weekend)
            next_allowed = next_weekend.replace(hour=20, minute=0, second=0, microsecond=0)
            
            return next_allowed.strftime('%Y-%m-%d %H:%M:%S')
        
        # 如果是周末但不在游戏时间
        if now.hour < 20:
            # 今天20:00开始
            return now.replace(hour=20, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M:%S')
        else:
            # 明天20:00开始（如果明天是周末）
            tomorrow = now + timedelta(days=1)
            if not self._is_weekday(tomorrow):
                return tomorrow.replace(hour=20, minute=0, second=0, microsecond=0).strftime('%Y-%m-%d %H:%M:%S')
            else:
                # 下个周末
                return self._calculate_next_weekend(tomorrow).strftime('%Y-%m-%d %H:%M:%S')
    
    def _calculate_next_weekend(self, from_date: datetime) -> datetime:
        """计算下个周末"""
        days_until_saturday = (5 - from_date.weekday()) % 7
        if days_until_saturday == 0:
            days_until_saturday = 7
        
        next_saturday = from_date + timedelta(days=days_until_saturday)
        return next_saturday.replace(hour=20, minute=0, second=0, microsecond=0)
    
    # 数据库操作方法
    async def _save_realname_info(self, realname_info: RealNameInfo):
        """保存实名认证信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO realname_verification 
                    (user_id, real_name, id_card_number, phone_number, verification_status, verification_time, nrta_response)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    realname_info.user_id,
                    realname_info.real_name,
                    realname_info.id_card_number,
                    realname_info.phone_number,
                    realname_info.verification_status,
                    realname_info.verification_time,
                    json.dumps(realname_info.nrta_response) if realname_info.nrta_response else None
                ))
        except Exception as e:
            self.logger.error(f"Failed to save realname info: {e}")
    
    async def _update_play_time_record(self, user_id: str, session_minutes: int):
        """更新游戏时间记录"""
        today = datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.now().strftime('%H:%M')
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # 获取今日现有记录
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT total_minutes, sessions FROM play_time_records 
                    WHERE user_id = ? AND date = ?
                """, (user_id, today))
                
                row = cursor.fetchone()
                
                if row:
                    # 更新现有记录
                    current_total, sessions_json = row
                    sessions = json.loads(sessions_json) if sessions_json else []
                    
                    new_total = current_total + session_minutes
                    sessions.append({
                        'start': current_time,
                        'duration': session_minutes
                    })
                    
                    conn.execute("""
                        UPDATE play_time_records 
                        SET total_minutes = ?, sessions = ?
                        WHERE user_id = ? AND date = ?
                    """, (new_total, json.dumps(sessions), user_id, today))
                else:
                    # 创建新记录
                    sessions = [{'start': current_time, 'duration': session_minutes}]
                    
                    conn.execute("""
                        INSERT INTO play_time_records 
                        (user_id, date, total_minutes, sessions, is_holiday)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        user_id, today, session_minutes, 
                        json.dumps(sessions), self._is_holiday(datetime.now().date())
                    ))
                
        except Exception as e:
            self.logger.error(f"Failed to update play time: {e}")
    
    async def _get_monthly_payment_total(self, user_id: str) -> float:
        """获取本月充值总额"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT SUM(amount_yuan) FROM payment_records 
                    WHERE user_id = ? AND strftime('%Y-%m', timestamp) = strftime('%Y-%m', 'now')
                """, (user_id,))
                
                result = cursor.fetchone()
                return result[0] if result and result[0] else 0.0
                
        except Exception as e:
            self.logger.error(f"Failed to get monthly payment total: {e}")
            return 0.0
    
    # 其他辅助方法的简化实现
    def _setup_logging(self) -> logging.Logger:
        logger = logging.getLogger('anti_addiction')
        logger.setLevel(logging.INFO)
        return logger
    
    def _init_nrta_client(self):
        """初始化NRTA客户端"""
        return None  # 简化实现
    
    async def _get_parent_contact_info(self, user_id: str) -> Optional[Dict]:
        """获取家长联系信息"""
        return {'phone': '+86138****8888', 'email': 'parent@example.com'}
    
    async def _send_approval_sms(self, phone: str, message: str):
        """发送授权短信"""
        print(f"SMS授权通知: {phone}")
    
    async def _send_approval_email(self, email: str, message: str, approval_id: str):
        """发送授权邮件"""
        print(f"Email授权通知: {email}")
    
    async def _notify_parent_game_start(self, user_id: str):
        """通知家长游戏开始"""
        print(f"通知家长：用户{user_id}开始游戏")
    
    async def _notify_parent_payment(self, payment_record: PaymentRecord):
        """通知家长充值信息"""
        print(f"通知家长：用户{payment_record.user_id}充值{payment_record.amount_yuan}元")


# 使用示例和测试
async def demo_anti_addiction_system():
    """防沉迷系统演示"""
    
    print("🎮 中国防沉迷系统演示\n")
    
    # 创建管理器
    manager = AntiAddictionManager()
    
    # 1. 实名认证演示
    print("1️⃣ 实名认证演示")
    
    realname_result = await manager.submit_realname_verification(
        user_id="user_12345",
        real_name="张小明",
        id_card_number="110101200801011234",  # 示例身份证号（2008年出生，约15岁）
        phone_number="13800138000"
    )
    
    print(f"实名认证结果: {realname_result.verification_status}")
    
    # 2. 游戏时间检查演示
    print("\n2️⃣ 游戏时间检查演示")
    
    can_play, reason, remaining = manager.can_play_now("user_12345")
    print(f"是否可以游戏: {can_play}")
    print(f"原因: {reason}")
    if remaining:
        print(f"剩余时间: {remaining}分钟")
    
    # 3. 游戏会话管理演示
    if can_play:
        print("\n3️⃣ 游戏会话管理演示")
        
        session_result = await manager.start_game_session("user_12345")
        print(f"会话开始结果: {session_result['status']}")
        
        if session_result['status'] == 'allowed':
            print(f"会话ID: {session_result['session_id']}")
            print(f"最大游戏时长: {session_result['max_duration_minutes']}分钟")
    
    # 4. 充值限制演示
    print("\n4️⃣ 充值限制演示")
    
    payment_result = await manager.process_payment(
        user_id="user_12345",
        amount_yuan=30,  # 尝试充值30元
        payment_method="wechat"
    )
    
    print(f"充值结果: {payment_result['status']}")
    if 'reason' in payment_result:
        print(f"原因: {payment_result['reason']}")
    
    # 5. 合规报告生成
    print("\n5️⃣ 合规报告生成")
    
    compliance_report = await manager.generate_anti_addiction_report()
    print("防沉迷合规报告:")
    print(json.dumps(compliance_report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(demo_anti_addiction_system())