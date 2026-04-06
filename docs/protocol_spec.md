# 🔐 Đuka Protocol Specification v0.1

> Distributed Unified Knowledge Architecture — Communication Protocol

---

## 📋 Overview

This document defines the wire protocol for communication between Đuka nodes.

### Design Goals
- ✅ Minimal & extensible message format
- ✅ Secure by default (auth + encryption)
- ✅ Efficient for both LAN and WAN
- ✅ Eventual consistency for shared knowledge

---

## 📦 Message Format

All messages use JSON envelope with the following structure:

```json
{
  "msg_id": "uuid4-string",
  "type": "heartbeat|insight_share|query|response|command|error",
  "sender": "node_id_string",
  "timestamp": 1712345678.123,
  "payload": { ... },
  "signature": "optional_ed25519_signature"
}
