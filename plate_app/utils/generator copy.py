from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import math
import os

class PlateTemplateGenerator:
    def __init__(self):
        self.CONTROL_WELLS = [''A1', 'B1', 'C1', 'D1','E1','F1''] 
        self.WELLS_PER_PLATE = 96
        self.SAMPLES_PER_PLATE = 90  # 96 - 6 control wells
        
    def mm(self, mm):
        """Convert millimeters to points."""
        return mm / 0.352777778
        
    def calculate_plates_needed(self, total_samples):
        """Calculate number of plates needed for given sample count."""
        return math.ceil(total_samples / self.SAMPLES_PER_PLATE)
        
    def get_well_coordinates(self, plate_number):
        """Get base coordinates for a plate based on its position (1 or 2)."""
        if plate_number == 1:
            return {
                'x_start': 20,
                'y_start': 192,
                'col_pos_ini': 34.38,  # 20 + 14.38
                'lin_pos_ini': 265.76  # 297 - 20 - 11.24
            }
        else:
            return {
                'x_start': 20,  # Mesmo x_start da primeira placa
                'y_start': 50,  # Ajustado para evitar sobreposição
                'col_pos_ini': 34.38,  # Mesmo col_pos_ini da primeira placa
                'lin_pos_ini': 123.76  # Ajustado para manter proporção com novo y_start
            }
    
    def draw_plate_grid(self, c, coords, sample_counter, total_samples):
        """Draw a single plate grid with wells and numbers."""
        # Draw plate outline
        c.roundRect(self.mm(coords['x_start']), self.mm(coords['y_start']), 
                   self.mm(127.76), self.mm(85.48), self.mm(5))
        
        # Setup initial positions
        col_pos_ini = coords['col_pos_ini']
        lin_pos_ini = coords['lin_pos_ini']
        diametro = 4.5
        
        # Draw column headers (01-12)
        c.setFont("Helvetica", 7)
        for i in range(12):
            c.drawCentredString(self.mm(col_pos_ini + diametro * (i*2)),
                              self.mm(lin_pos_ini + 6),
                              f"{i+1:02d}")
        
        # Draw row headers (A-H)
        rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        for i, row in enumerate(rows):
            c.drawCentredString(self.mm(col_pos_ini - 8),
                              self.mm(lin_pos_ini - 1.5 - diametro * (i*2)),
                              row)
        
        # Draw wells and numbers
        current_sample = sample_counter
        for row in range(8):
            for col in range(12):
                x = col_pos_ini + diametro * (col*2)
                y = lin_pos_ini + diametro * (-row*2)
                
                well_id = f"{rows[row]}{col+1}"
                if well_id in self.CONTROL_WELLS:
                    # Control well - red
                    c.setFillColorRGB(1, 0, 0)
                    c.circle(self.mm(x), self.mm(y), self.mm(diametro-0.50), fill=1)
                else:
                    # Sample well - white with number
                    if current_sample <= total_samples:
                        c.setFillColorRGB(1, 1, 1)
                        c.circle(self.mm(x), self.mm(y), self.mm(diametro-0.50), fill=1)
                        c.setFillColorRGB(0, 0, 0)
                        c.setFont("Helvetica", 6)
                        c.drawCentredString(self.mm(x), self.mm(y-1), str(current_sample))
                        current_sample += 1
                    else:
                        # Empty well - white
                        c.setFillColorRGB(1, 1, 1)
                        c.circle(self.mm(x), self.mm(y), self.mm(diametro-0.50), fill=1)
        
        return current_sample
    
    def draw_plate_info(self, c, coords, plate_data, cod_envio):
        """Draw plate identification and information."""
        # Draw plate ID
        c.setFont("Courier", 20)
        x = coords['x_start'] + 5
        y = coords['y_start'] - 15
        plate_id = f"{plate_data['empresa']}-{plate_data['projeto']}-{plate_data['placa']:03d}"
        c.drawString(self.mm(x), self.mm(y+5), plate_id)
        
        # Draw labels
        c.setFont("Courier", 10)
        c.drawString(self.mm(x), self.mm(y), "EMPRESA-PROJETO-PLACA")
        c.drawString(self.mm(x+70), self.mm(y+5), f"COD.ENVIO LAB: {cod_envio}")
    
    def generate_pdf(self, output_path, project_data, cod_envio):
        """Generate PDF with plate templates based on project data."""
        total_samples = project_data['total_amostras']
        total_plates = self.calculate_plates_needed(total_samples)
        total_pages = math.ceil(total_plates / 2)
        
        c = canvas.Canvas(output_path, pagesize=A4)
        
        current_sample = 1
        for page in range(total_pages):
            # Draw page border
            c.rect(self.mm(1), self.mm(1), self.mm(208), self.mm(295))
            
            # First plate on page
            if current_sample <= total_samples:
                coords1 = self.get_well_coordinates(1)
                project_data['placa'] = (page * 2) + 1
                self.draw_plate_info(c, coords1, project_data, cod_envio)
                current_sample = self.draw_plate_grid(c, coords1, current_sample, total_samples)
            
            # Second plate on page
            if current_sample <= total_samples:
                coords2 = self.get_well_coordinates(2)
                project_data['placa'] = (page * 2) + 2
                self.draw_plate_info(c, coords2, project_data, cod_envio)
                current_sample = self.draw_plate_grid(c, coords2, current_sample, total_samples)
            
            c.showPage()
        
        c.save()