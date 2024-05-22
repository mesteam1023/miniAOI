import segno
import openpyxl

# Define variable to load the dataframe
dataframe = openpyxl.load_workbook("test.xlsx")

# Define variable to read sheet
dataframe1 = dataframe.active

# Iterate the loop to read the cell values
for row in range(0, dataframe1.max_row):
    row_value = []
    for col in dataframe1.iter_cols(1, dataframe1.max_column):
        print(col[row].value)
        row_value.append(col[row].value)
    qrcode = segno.make_qr(row_value)
    qrcode.save(f'{row_value}.png')