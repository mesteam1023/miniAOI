import subprocess
import asyncio
from flask_cors import CORS
from flask import Flask, render_template,request
from menu import menu,take_sample,TakeCoordinates
from async_checking import async_checking


app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    # result = await async_checking()
    return 'Hello World'

@app.route('/test')
def test():
    try:
        # Replace 'your_command_here' with the actual command you want to run
        result = subprocess.check_output(['python3','main.py','0'], shell=True, stderr=subprocess.STDOUT)
        return f"Command executed successfully: {result.decode('utf-8')}"
    except subprocess.CalledProcessError as e:
        return f"Error executing command: {e.output.decode('utf-8')}"

@app.route('/takeSample')
async def takeSample():
    partNo = request.args.get('partNo')
    await take_sample()
    await TakeCoordinates(partNo)
    return 'Finish!'

@app.route('/visualInspection')
async def visualInspection():          
    result = async_checking()
    return await asyncio.create_task(result)

def main():
    try:
       app.run(debug = True, host='0.0.0.0')
    except KeyboardInterrupt as e:
        print("out")

# if __name__ == '__main__':
    # app.run(debug=True, host='0.0.0.0')
main()
