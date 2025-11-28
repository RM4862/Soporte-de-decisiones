import sys
import traceback

try:
    import os
    from rayleigh_api import APP
    print("✅ Flask app imported successfully")
    print("🚀 Starting Flask server...")
    port = int(os.getenv('PORT', 5000))
    APP.run(host='0.0.0.0', port=port, debug=False)
except Exception as e:
    print(f"❌ Error starting Flask:")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    traceback.print_exc()
    sys.exit(1)
