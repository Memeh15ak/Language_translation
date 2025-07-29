from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfutils
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import sys
import os

def txt_to_pdf(txt_file_path, pdf_file_path=None):
    """
    Convert a text file to PDF format.
    
    Args:
        txt_file_path (str): Path to the input .txt file
        pdf_file_path (str): Path for output .pdf file (optional)
    """
    
    if pdf_file_path is None:
        base_name = os.path.splitext(txt_file_path)[0]
        pdf_file_path = base_name + '.pdf'
    
    try:
        with open(txt_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        c = canvas.Canvas(pdf_file_path, pagesize=letter)
        width, height = letter
        
        try:
            hindi_fonts = [
                'C:/Windows/Fonts/mangal.ttf',      
                'C:/Windows/Fonts/kokila.ttf',        
                'C:/Windows/Fonts/aparaj.ttf',      
                'C:/Windows/Fonts/nirmala.ttf',     
                'C:/Windows/Fonts/utsaah.ttf',      
            ]
            
            font_registered = False
            for font_path in hindi_fonts:
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont('HindiFont', font_path))
                        c.setFont('HindiFont', 12)
                        font_registered = True
                        print(f"Using font: {font_path}")
                        break
                    except:
                        continue
            
            if not font_registered:
                print("Warning: No Hindi font found. Using default font (may not display Hindi properly)")
                c.setFont('Helvetica', 12)
        except:
            print("Warning: Font registration failed. Using default font")
            c.setFont('Helvetica', 12)
        
        margin_left = 72  
        margin_right = 72  
        margin_top = 72   
        margin_bottom = 72  
        
        y_position = height - margin_top
        line_height = 14
        max_width = width - margin_left - margin_right
        
        lines = content.split('\n')
        
        for line in lines:
            if c.stringWidth(line) > max_width:
                words = line.split(' ')
                current_line = ""
                
                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    try:
                        test_width = c.stringWidth(test_line)
                    except:
                        test_width = len(test_line) * 7  
                    
                    if test_width <= max_width:
                        current_line = test_line
                    else:
                        if current_line:
                            try:
                                c.drawString(margin_left, y_position, current_line)
                            except:
                                c.drawString(margin_left, y_position, current_line.encode('utf-8', errors='ignore').decode('utf-8'))
                            y_position -= line_height
                            
                            if y_position < margin_bottom:
                                c.showPage()
                                if 'font_registered' in locals() and font_registered:
                                    c.setFont('HindiFont', 12)
                                else:
                                    c.setFont('Helvetica', 12)
                                y_position = height - margin_top
                        
                        current_line = word
                
                if current_line:
                    try:
                        c.drawString(margin_left, y_position, current_line)
                    except:
                        c.drawString(margin_left, y_position, current_line.encode('utf-8', errors='ignore').decode('utf-8'))
                    y_position -= line_height
            else:
    
                try:
                    c.drawString(margin_left, y_position, line)
                except:
                    c.drawString(margin_left, y_position, line.encode('utf-8', errors='ignore').decode('utf-8'))
                y_position -= line_height
        
            if y_position < margin_bottom:
                c.showPage()
                if 'font_registered' in locals() and font_registered:
                    c.setFont('HindiFont', 12)
                else:
                    c.setFont('Helvetica', 12)
                y_position = height - margin_top
    
        c.save()
        print(f"Successfully converted '{txt_file_path}' to '{pdf_file_path}'")
        
    except FileNotFoundError:
        print(f"Error: File '{txt_file_path}' not found.")
    except Exception as e:
        print(f"Error converting file: {str(e)}")

def main():
    """Main function to handle command line usage"""
    
    input_file = "translated_output.txt"
    output_file = "final.pdf"
    
    txt_to_pdf(input_file, output_file)

if __name__ == "__main__":
    main()
