#!/usr/bin/env python3
"""
企业级配置管理
Enterprise Configuration Management

统一管理整个合规系统的配置参数：
- 数据库连接
- API认证密钥
- 第三方服务集成
- 法规更新源
- 通知设置
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import timedelta

class ComplianceSystemConfig:
    """合规系统配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.project_root = Path(__file__).parent
        self.config_file = config_file or (self.project_root / "config" / "system.yaml")
        
        # 确保配置目录存在
        self.config_file.parent.mkdir(exist_ok=True)
        
        # 加载配置
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        
        # 默认配置
        default_config = self._get_default_config()
        
        # 如果配置文件存在，加载并合并
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = yaml.safe_load(f) or {}
                
                # 深度合并配置
                return self._deep_merge(default_config, file_config)
                
            except Exception as e:
                print(f"⚠️ 配置文件加载失败，使用默认配置: {e}")
        
        return default_config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            # 系统基础配置
            'system': {
                'version': '2.0.0',
                'environment': 'development',  # development, staging, production
                'debug_mode': True,
                'log_level': 'INFO',
                'timezone': 'UTC'
            },
            
            # 数据库配置
            'database': {
                'type': 'sqlite',  # sqlite, postgresql, mysql
                'path': 'data/',
                'files': {
                    'compliance': 'compliance.db',
                    'anti_addiction': 'anti_addiction.db',
                    'gdpr_rights': 'gdpr_rights.db'
                },
                'backup': {
                    'enabled': True,
                    'frequency': 'daily',  # hourly, daily, weekly
                    'retention_days': 30
                },
                'connection_pool': {
                    'max_connections': 10,
                    'timeout_seconds': 30
                }
            },
            
            # API服务器配置
            'api': {
                'host': '0.0.0.0',
                'port': 5000,
                'cors_enabled': True,
                'cors_origins': ['http://localhost:3000', 'https://yourdomain.com'],
                'authentication': {
                    'enabled': True,
                    'api_keys': {
                        # 在生产环境中应该从环境变量加载
                        'demo-key': 'Demo access key',
                        'admin-key': 'Administrative access'
                    },
                    'jwt': {
                        'enabled': False,
                        'secret_key': 'your-jwt-secret-key',
                        'expiration_hours': 24
                    }
                },
                'rate_limiting': {
                    'enabled': True,
                    'default_limits': {
                        'per_minute': 60,
                        'per_hour': 1000,
                        'per_day': 10000
                    },
                    'premium_limits': {
                        'per_minute': 300,
                        'per_hour': 5000,
                        'per_day': 50000
                    }
                }
            },
            
            # 缓存配置
            'cache': {
                'enabled': True,
                'backend': 'memory',  # memory, redis, memcached
                'ttl_seconds': 3600,
                'redis': {
                    'host': 'localhost',
                    'port': 6379,
                    'db': 0,
                    'password': None
                },
                'rules_cache_ttl': 1800,  # 规则缓存30分钟
                'analysis_cache_ttl': 300   # 分析结果缓存5分钟
            },
            
            # 法规数据源配置
            'regulatory_sources': {
                'auto_update': True,
                'update_frequency': 'weekly',
                'sources': {
                    'coppa': {
                        'url': 'https://www.ftc.gov/enforcement/rules/rulemaking-regulatory-reform-proceedings/childrens-online-privacy-protection-rule',
                        'last_check': None
                    },
                    'gdpr': {
                        'url': 'https://gdpr-info.eu/',
                        'last_check': None
                    },
                    'china_gaming': {
                        'url': 'http://www.nrta.gov.cn/',
                        'last_check': None
                    }
                }
            },
            
            # 第三方服务集成
            'third_party_services': {
                # NRTA实名认证
                'nrta': {
                    'enabled': False,
                    'endpoint': 'https://api.nrta.gov.cn/realname/verify',
                    'app_id': 'your_nrta_app_id',
                    'secret_key': 'your_nrta_secret',
                    'timeout_seconds': 10,
                    'retry_attempts': 3
                },
                
                # 支付处理器（COPPA信用卡验证）
                'payment_processor': {
                    'provider': 'stripe',  # stripe, paypal, square
                    'api_key': 'your_payment_api_key',
                    'webhook_secret': 'your_webhook_secret',
                    'test_mode': True
                },
                
                # 邮件服务
                'email': {
                    'provider': 'smtp',  # smtp, sendgrid, ses
                    'smtp': {
                        'host': 'smtp.gmail.com',
                        'port': 587,
                        'username': 'your_email@gmail.com',
                        'password': 'your_email_password',
                        'use_tls': True
                    },
                    'from_address': 'noreply@yourdomain.com',
                    'from_name': 'Compliance System'
                },
                
                # 短信服务
                'sms': {
                    'provider': 'twilio',  # twilio, aws_sns
                    'account_sid': 'your_twilio_sid',
                    'auth_token': 'your_twilio_token',
                    'from_number': '+1234567890'
                },
                
                # 身份验证服务
                'identity_verification': {
                    'provider': 'jumio',  # jumio, onfido
                    'api_key': 'your_identity_api_key',
                    'api_secret': 'your_identity_secret'
                }
            },
            
            # 通知配置
            'notifications': {
                'enabled': True,
                'channels': ['email', 'sms'],
                'templates': {
                    'request_received': {
                        'subject': '数据主体权利请求已收到',
                        'template_file': 'templates/notifications/request_received.html'
                    },
                    'request_completed': {
                        'subject': '数据主体权利请求已完成',
                        'template_file': 'templates/notifications/request_completed.html'
                    }
                },
                'retry_policy': {
                    'max_retries': 3,
                    'retry_delay_seconds': 60
                }
            },
            
            # 安全配置
            'security': {
                'data_encryption': {
                    'enabled': True,
                    'algorithm': 'AES-256-GCM',
                    'key_rotation_days': 90
                },
                'audit_logging': {
                    'enabled': True,
                    'log_file': 'logs/audit.log',
                    'retention_days': 2555  # 7 years
                },
                'session_management': {
                    'timeout_minutes': 30,
                    'max_concurrent_sessions': 5
                },
                'ip_whitelist': {
                    'enabled': False,
                    'allowed_ips': []
                }
            },
            
            # 报告和分析配置
            'reporting': {
                'auto_generate': True,
                'formats': ['html', 'pdf', 'json'],
                'storage': {
                    'local_path': 'reports/',
                    's3_bucket': None,  # 如果使用S3存储
                    'retention_days': 365
                },
                'templates': {
                    'executive_summary': 'templates/reports/executive_summary.html',
                    'technical_report': 'templates/reports/technical_report.html',
                    'compliance_audit': 'templates/reports/compliance_audit.html'
                }
            },
            
            # 监控和告警
            'monitoring': {
                'enabled': True,
                'metrics_collection': True,
                'health_check_interval': 60,
                'alerts': {
                    'email_recipients': ['admin@yourdomain.com'],
                    'thresholds': {
                        'api_error_rate': 0.05,  # 5% 错误率
                        'response_time_ms': 2000,
                        'memory_usage_percent': 85,
                        'disk_usage_percent': 90
                    }
                }
            },
            
            # 合规规则配置
            'compliance_rules': {
                'auto_reload': True,
                'reload_interval_minutes': 15,
                'rules_file': 'config/compliance-rules.yaml',
                'custom_rules_dir': 'config/custom_rules/',
                'validation': {
                    'strict_mode': True,
                    'require_legal_basis': True,
                    'require_implementation_guide': True
                }
            },
            
            # 数据保留政策
            'data_retention': {
                'default_retention_years': 7,
                'categories': {
                    'audit_logs': {'years': 7, 'auto_delete': False},
                    'user_requests': {'years': 7, 'auto_delete': False},
                    'compliance_reports': {'years': 5, 'auto_delete': True},
                    'cache_data': {'hours': 24, 'auto_delete': True},
                    'session_logs': {'days': 90, 'auto_delete': True}
                },
                'deletion_schedule': {
                    'enabled': True,
                    'run_frequency': 'weekly',
                    'run_time': '02:00'  # 凌晨2点
                }
            },
            
            # 国际化配置
            'i18n': {
                'default_language': 'zh-CN',
                'supported_languages': ['zh-CN', 'en-US', 'ja-JP', 'ko-KR'],
                'auto_detect': True,
                'translations_dir': 'locales/'
            }
        }
    
    def _deep_merge(self, base: Dict, update: Dict) -> Dict:
        """深度合并字典"""
        result = base.copy()
        
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get(self, key_path: str, default=None):
        """获取配置值（支持点路径）"""
        keys = key_path.split('.')
        current = self.config
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current
    
    def set(self, key_path: str, value):
        """设置配置值"""
        keys = key_path.split('.')
        current = self.config
        
        for key in keys[:-1]:
            if key not in current or not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def save(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            
            print(f"✅ 配置已保存到 {self.config_file}")
            
        except Exception as e:
            print(f"❌ 配置保存失败: {e}")
    
    def validate(self) -> bool:
        """验证配置完整性"""
        required_keys = [
            'system.version',
            'database.type',
            'api.host',
            'api.port'
        ]
        
        missing_keys = []
        
        for key in required_keys:
            if self.get(key) is None:
                missing_keys.append(key)
        
        if missing_keys:
            print(f"❌ 缺少必需配置项: {', '.join(missing_keys)}")
            return False
        
        return True
    
    def get_database_url(self, db_name: str) -> str:
        """获取数据库连接URL"""
        db_type = self.get('database.type')
        
        if db_type == 'sqlite':
            db_path = Path(self.get('database.path')) / self.get(f'database.files.{db_name}')
            return f"sqlite:///{db_path}"
        
        elif db_type == 'postgresql':
            host = self.get('database.postgresql.host', 'localhost')
            port = self.get('database.postgresql.port', 5432)
            username = self.get('database.postgresql.username')
            password = self.get('database.postgresql.password')
            database = self.get('database.postgresql.database')
            
            return f"postgresql://{username}:{password}@{host}:{port}/{database}"
        
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def is_production(self) -> bool:
        """检查是否生产环境"""
        return self.get('system.environment') == 'production'
    
    def is_debug_enabled(self) -> bool:
        """检查是否启用调试模式"""
        return self.get('system.debug_mode', False)
    
    def get_api_keys(self) -> Dict[str, str]:
        """获取API密钥"""
        api_keys = self.get('api.authentication.api_keys', {})
        
        # 从环境变量加载生产密钥
        if self.is_production():
            env_keys = {}
            for key, desc in api_keys.items():
                env_var = f"COMPLIANCE_API_KEY_{key.upper().replace('-', '_')}"
                env_value = os.getenv(env_var)
                if env_value:
                    env_keys[key] = env_value
            
            return env_keys
        
        return api_keys
    
    def export_config_template(self, file_path: str = None):
        """导出配置模板"""
        template_path = file_path or (self.project_root / "config" / "system-template.yaml")
        template_path.parent.mkdir(exist_ok=True)
        
        # 创建配置模板（移除敏感信息）
        template_config = self.config.copy()
        
        # 清空敏感配置
        template_config['third_party_services']['nrta']['secret_key'] = 'YOUR_NRTA_SECRET_KEY'
        template_config['third_party_services']['payment_processor']['api_key'] = 'YOUR_PAYMENT_API_KEY'
        template_config['third_party_services']['email']['smtp']['password'] = 'YOUR_EMAIL_PASSWORD'
        template_config['third_party_services']['sms']['auth_token'] = 'YOUR_TWILIO_TOKEN'
        
        try:
            with open(template_path, 'w', encoding='utf-8') as f:
                yaml.dump(template_config, f, default_flow_style=False, allow_unicode=True)
            
            print(f"✅ 配置模板已导出到 {template_path}")
            
        except Exception as e:
            print(f"❌ 配置模板导出失败: {e}")

# 全局配置实例
config = ComplianceSystemConfig()

# 便捷访问函数
def get_config(key: str, default=None):
    """获取配置值"""
    return config.get(key, default)

def is_production():
    """检查是否生产环境"""
    return config.is_production()

def is_debug():
    """检查是否调试模式"""  
    return config.is_debug_enabled()

def get_database_url(db_name: str):
    """获取数据库URL"""
    return config.get_database_url(db_name)

# 使用示例
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="合规系统配置管理")
    parser.add_argument('--validate', action='store_true', help='验证配置')
    parser.add_argument('--export-template', help='导出配置模板')
    parser.add_argument('--get', help='获取配置值')
    parser.add_argument('--set', nargs=2, metavar=('KEY', 'VALUE'), help='设置配置值')
    
    args = parser.parse_args()
    
    if args.validate:
        if config.validate():
            print("✅ 配置验证通过")
        else:
            print("❌ 配置验证失败")
    
    elif args.export_template:
        config.export_config_template(args.export_template)
    
    elif args.get:
        value = config.get(args.get)
        print(f"{args.get} = {value}")
    
    elif args.set:
        key, value = args.set
        # 尝试解析JSON值
        try:
            value = json.loads(value)
        except:
            pass
        
        config.set(key, value)
        config.save()
        print(f"✅ 已设置 {key} = {value}")
    
    else:
        print("📋 合规系统配置信息")
        print(f"版本: {config.get('system.version')}")
        print(f"环境: {config.get('system.environment')}")  
        print(f"配置文件: {config.config_file}")
        print(f"调试模式: {config.is_debug_enabled()}")
        print(f"数据库类型: {config.get('database.type')}")
        print(f"API端口: {config.get('api.port')}")
        print(f"缓存启用: {config.get('cache.enabled')}")
        print(f"监控启用: {config.get('monitoring.enabled')}")