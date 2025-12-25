import asyncio
import logging
import sys
import os

# Ensure backend directory is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Force UTF-8 encoding for Windows console
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Load env vars
from dotenv import load_dotenv
load_dotenv(os.path.join(current_dir, ".env"))

try:
    from app.core.scheduler import sync_realtime_scores_job
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

async def main():
    print("🚀 Starting sync_realtime_scores_job test...")
    try:
        await sync_realtime_scores_job()
        print("✅ Job completed successfully.")
    except Exception as e:
        print(f"❌ Job failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Fix for Windows asyncio loop
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    asyncio.run(main())
