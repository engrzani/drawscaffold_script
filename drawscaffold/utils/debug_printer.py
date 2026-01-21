class DebugPrinter:
    def __init__(self, debug_mode: bool):
        self.debug_mode = debug_mode

    def print(self, obj):
        if self.debug_mode:
            import sys
            try:
                print(str(obj))
            except UnicodeEncodeError:
                sys.stdout.buffer.write((str(obj) + '\n').encode('utf-8', errors='replace'))
