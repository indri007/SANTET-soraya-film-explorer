#!/usr/bin/env python3
"""
bit_daemon.py
Daemon Layanan Pemroses Bahasa Bit (Binary Octet Stream Daemon)
Mendukung enkoding otomatis string/file ke bahasa bit 8-bit UTF-8,
validasi checksum SHA-256, dan pencatatan log daemon.
"""

import sys
import os
import time
import json
import hashlib
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "output")
DAEMON_LOG = os.path.join(LOG_DIR, "bit_daemon.log")
STATUS_FILE = os.path.join(LOG_DIR, "bit_daemon_status.json")

os.makedirs(LOG_DIR, exist_ok=True)

def text_to_bits(text: str) -> str:
    utf8_bytes = text.encode("utf-8")
    return " ".join(f"{b:08b}" for b in utf8_bytes)

def bits_to_text(bit_string: str) -> str:
    bits_list = bit_string.split()
    byte_arr = bytearray(int(b, 2) for b in bits_list)
    return byte_arr.decode("utf-8")

def log_event(event_type: str, payload_summary: str, bit_len: int, sha256_hash: str):
    timestamp = datetime.now().isoformat()
    log_line = f"[{timestamp}] [{event_type}] Bits: {bit_len} | SHA256: {sha256_hash[:16]}... | {payload_summary}\n"
    with open(DAEMON_LOG, "a", encoding="utf-8") as f:
        f.write(log_line)

def run_daemon_tick():
    # Periksa status daemon dan buat manifest biner
    status = {
        "daemon_name": "BIT_STREAM_DAEMON_V1",
        "state": "ACTIVE",
        "protocol": "UTF-8_8BIT_OCTET",
        "last_heartbeat": datetime.now().isoformat(),
        "pid": os.getpid(),
        "status_message": "NodeXL file archived; Bit daemon standby for network/data payloads."
    }
    
    # Generate bit version of daemon status
    json_str = json.dumps(status, indent=2)
    bit_representation = text_to_bits(json_str)
    sha256_val = hashlib.sha256(json_str.encode("utf-8")).hexdigest()
    
    status["sha256"] = sha256_val
    status["total_bits"] = len(bit_representation.replace(" ", ""))
    status["total_bytes"] = len(json_str.encode("utf-8"))
    
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2)
        
    bit_status_file = os.path.join(LOG_DIR, "bit_daemon_status.bin.txt")
    with open(bit_status_file, "w", encoding="utf-8") as f:
        f.write(bit_representation)
        
    log_event("STATUS_SYNC", "Status daemon dikonversi ke bitstream", status["total_bits"], sha256_val)
    return status, bit_representation

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--encode":
        text = sys.argv[2] if len(sys.argv) > 2 else sys.stdin.read()
        print(text_to_bits(text))
        return
        
    if len(sys.argv) > 1 and sys.argv[1] == "--decode":
        bits = sys.argv[2] if len(sys.argv) > 2 else sys.stdin.read()
        print(bits_to_text(bits))
        return

    # Default run: Inisialisasi status daemon dalam bahasa bit
    status, bits = run_daemon_tick()
    print("=" * 60)
    print("      BIT STREAM DAEMON - RUNTIME STATUS")
    print("=" * 60)
    print(f"Status Service      : {status['state']}")
    print(f"PID                 : {status['pid']}")
    print(f"Protokol            : {status['protocol']}")
    print(f"Total Byte Status   : {status['total_bytes']} bytes")
    print(f"Total Bit Stream    : {status['total_bits']} bits")
    print(f"SHA-256 Checksum    : {status['sha256']}")
    print(f"Status File (JSON)  : {STATUS_FILE}")
    print(f"Status File (Bit)   : {os.path.join(LOG_DIR, 'bit_daemon_status.bin.txt')}")
    print(f"Daemon Event Log    : {DAEMON_LOG}")
    print("=" * 60)

if __name__ == "__main__":
    main()
