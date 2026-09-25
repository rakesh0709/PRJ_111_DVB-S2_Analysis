import sys, os
import win32com.client

with open("build_ieee_docx.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

def run_test(target_line, name):
    print(f"\n--- Testing up to line {target_line} ({name}) ---", flush=True)
    sub = "".join(lines[:target_line]) + f"\n    doc.save('{name}.docx')\nbuild_paper()\n"
    with open("temp_sub.py", "w", encoding="utf-8") as tf:
        tf.write(sub)
    ret = os.system(f'"{sys.executable}" temp_sub.py')
    if ret != 0:
        print(f"Script failed with code {ret}", flush=True)
        return False
    
    print(f"Generated {name}.docx ({os.path.getsize(name+'.docx')} bytes). Opening in Word...", flush=True)
    word = win32com.client.DispatchEx('Word.Application')
    word.Visible = False
    word.DisplayAlerts = 0
    try:
        doc = word.Documents.Open(os.path.abspath(f"{name}.docx"), ReadOnly=True)
        pages = doc.ComputeStatistics(2)
        print(f"SUCCESS! Word opened {name}.docx! Pages: {pages}", flush=True)
        doc.Close(False)
        return True
    except Exception as e:
        print(f"FAILED to open: {e}", flush=True)
        return False
    finally:
        word.Quit()

if __name__ == "__main__":
    line_no = int(sys.argv[1])
    test_name = sys.argv[2]
    run_test(line_no, test_name)
