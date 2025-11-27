from flask import Flask, jsonify
import mysql.connector

app = Flask(__name__)

@app.route('/test', methods=['GET'])
def test():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='SG_Proyectos'
        )
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT COUNT(*) as total FROM Proyectos")
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'total_proyectos': result['total']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting test server...")
    app.run(host='0.0.0.0', port=5001, debug=False)
