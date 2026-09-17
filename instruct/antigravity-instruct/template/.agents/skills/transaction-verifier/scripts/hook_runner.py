import sys
event = sys.argv[1] if len(sys.argv) > 1 else "event"
print(f"[HOOK] Transaction lifecycle: {event}")
