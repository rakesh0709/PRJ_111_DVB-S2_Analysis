import win32com.client, os, time, sys

docx_path = os.path.abspath("PRJ_111_Research_Paper_Final.docx")
pdf_path = os.path.abspath("PRJ_111_Research_Paper_Final_docx_rendered.pdf")

print(f"Opening Word to convert {docx_path} -> {pdf_path}...", flush=True)
t0 = time.time()
word = win32com.client.DispatchEx("Word.Application")
word.Visible = False
word.DisplayAlerts = 0

try:
    doc = word.Documents.Open(docx_path, ReadOnly=True)
    pages = doc.ComputeStatistics(2)
    print(f"Document opened in {time.time()-t0:.2f}s! Total Pages: {pages}", flush=True)
    t1 = time.time()
    doc.SaveAs2(pdf_path, FileFormat=17) # 17 = wdFormatPDF
    print(f"PDF exported in {time.time()-t1:.2f}s! File size: {os.path.getsize(pdf_path)} bytes", flush=True)
    doc.Close(False)
except Exception as e:
    print(f"Error during conversion: {e}", file=sys.stderr, flush=True)
    sys.exit(1)
finally:
    word.Quit()

print(f"All done in {time.time()-t0:.2f}s!", flush=True)
