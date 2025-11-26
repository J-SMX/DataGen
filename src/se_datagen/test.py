import sys
import os


src_path = os.path.abspath(__file__)
src_path = str(src_path[:-1])
sys.path.append(src_path)

print(src_path)

# 16 + 15 = 31
# 7