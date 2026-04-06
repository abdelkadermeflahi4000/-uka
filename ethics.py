import asyncio          # ✅ FIX: كان مفقوداً — asyncio.create_task يرفع NameError
import time             # ✅ FIX: كان مفقوداً — time.time() في _log_violation
import logging
from enum import Enum, auto
from typing import Callable, List, Optional
from dataclasses import dataclass

# ✅ FIX: ĐukaMessage و ComponentType مستخدمَان في هذا الملف لكن لم يُستورَدا
from protocol import ĐukaMessage, ComponentType


class EthicalRule:
    """قاعدة أخلاقية قابلة للتطبيق"""

    def __init__(self, name: str, condition: Callable, action: str, severity: int):
        self.name = name
        self.condition = condition  # function(context) -> bool
        self.action = action        # "block" | "warn" | "log"
        self.severity = severity    # 1-10
        self.violations = 0

    def evaluate(self, context: dict) -> Optional[str]:
        if self.condition(context):
            self.violations += 1
            if self.action == "block":
                return f"❌ BLOCKED: {self.name}"
            elif self.action == "warn":
                logging.warning(f"⚠️ WARNING: {self.name}")
            return f"📝 LOGGED: {self.name}"
        return None


class ĐukaBio:
    """حارس الأخلاقيات والسلامة"""

    # قواعد أساسية غير قابلة للإزالة
    BASE_RULES = [
        EthicalRule(
            name="no_biological_harm",
            condition=lambda ctx: ctx.get('action_type') == 'biological_experiment',
            action="block",
            severity=10
        ),
        EthicalRule(
            name="human_oversight_required",
            condition=lambda ctx: ctx.get('decision_impact', 0) > 0.8,
            action="block",     # يحتاج موافقة بشرية
            severity=9
        ),
        EthicalRule(
            name="privacy_preservation",
            condition=lambda ctx: (
                ctx.get('data_type') in ['face', 'voice', 'location']
                and not ctx.get('encrypted', False)
            ),
            action="block",
            severity=8
        ),
    ]

    def __init__(self, node_id: str, custom_rules: Optional[List[EthicalRule]] = None):
        self.node_id = node_id
        # ✅ FIX: نسخ القواعد الأساسية بدلاً من الإشارة المشتركة (class-level mutation)
        self.rules = list(self.BASE_RULES) + (custom_rules or [])
        self.audit_log: List[dict] = []
        self._core = None

    def _bind_core(self, core):
        self._core = core

    def validate_action(self, action_context: dict) -> tuple:
        """التحقق من أن الإجراء متوافق أخلاقياً"""
        for rule in self.rules:
            result = rule.evaluate({**action_context, 'node_id': self.node_id})
            if result and "BLOCKED" in result:
                self._log_violation(action_context, rule, result)
                return False, result
        return True, None

    def _log_violation(self, context: dict, rule: EthicalRule, result: str):
        entry = {
            'timestamp': time.time(),   # ✅ يعمل الآن
            'node_id': self.node_id,
            'rule': rule.name,
            'context': context,
            'result': result
        }
        self.audit_log.append(entry)

        # إرسال تنبيه للشبكة إذا كان الانتهاك خطيراً
        if rule.severity >= 8 and self._core:
            alert_msg = ĐukaMessage(   # ✅ يعمل الآن — ĐukaMessage مستورد
                source=self.node_id,
                component=ComponentType.BIO,
                msg_type='ethics_alert',
                payload={'severity': rule.severity, 'details': entry}
            )
            asyncio.create_task(self._core.message_queue.put(alert_msg))  # ✅ يعمل الآن

    async def on_message(self, message: ĐukaMessage):
        """معالجة الرسائل الواردة — مطلوب للتسجيل في ĐukaCore"""
        if message.msg_type == 'validate_action':
            ok, reason = self.validate_action(message.payload)
            if not ok:
                logging.error(f"[BIO] Ethics violation from {message.source}: {reason}")
