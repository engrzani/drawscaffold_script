import subprocess
import os

def run_case(args, expected_files):
    cmd = [os.path.join('.venv', 'Scripts', 'python.exe'), 'top_down_main.py'] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    print('STDOUT:', result.stdout)
    print('STDERR:', result.stderr)
    for f in expected_files:
        if not os.path.exists(f):
            print(f'File not found: {f}')
        else:
            print(f'File exists: {f}')

if __name__ == "__main__":
    # Test case 1: Standard dimensions
    args1 = [
        '--facade', 'inset,300,2000,250,F',
        '--facade', 'outset,700,2000,250,F',
        '--facade', 'outset,350,1200,400,R',
        '--facade', 'inset,600,1200,400,R',
        '--facade', 'inset,400,2000,250,B',
        '--facade', 'inset,400,1200,400,L',
        '--facade', 'outset,600,1200,500,L',
        '--facade', 'inset,850,1200,100,L',
        '--height-in-cm', '2000',
        '--surface-slope', '12',
        '--image', '--dxf',
        '--output-id', '1'
    ]
    expected_files1 = [
        'project_top_down_1.png',
        'project_1.dxf',
        'project_1.jpg'
    ]
    run_case(args1, expected_files1)

    # Test case 2: Different dimensions
    args2 = [
        '--facade', 'inset,200,1500,200,F',
        '--facade', 'outset,500,1500,200,F',
        '--facade', 'outset,250,1000,300,R',
        '--facade', 'inset,400,1000,300,R',
        '--facade', 'inset,300,1500,200,B',
        '--facade', 'inset,300,1000,300,L',
        '--facade', 'outset,400,1000,350,L',
        '--facade', 'inset,600,1000,80,L',
        '--height-in-cm', '1500',
        '--surface-slope', '8',
        '--image', '--dxf',
        '--output-id', '2'
    ]
    expected_files2 = [
        'project_top_down_2.png',
        'project_2.dxf',
        'project_2.jpg'
    ]
    run_case(args2, expected_files2)
