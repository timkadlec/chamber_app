import pandas as pd

# Path to your Excel file
file_path = 'source.xlsx'  # Replace this with your actual file path

# Read the Excel file, assuming the first row contains headers
df = pd.read_excel(file_path)

# Extract only the required columns
required_columns = [
    "Příjmení", 
    "Jméno", 
    "Osobní čís.", 
    "Název oboru/specializace", 
    "Školitel", 
    "Oborová katedra"
]

# Create a new DataFrame with only these columns
df_filtered = df[required_columns]

# Check the result
print(df_filtered)

# Define a Student class
class Student:
    def __init__(self, prijmeni, jmeno, osobni_cislo, obor_specializace, skolitel, oborova_katedra):
        self.prijmeni = prijmeni
        self.jmeno = jmeno
        self.osobni_cislo = osobni_cislo
        self.obor_specializace = obor_specializace
        self.skolitel = skolitel
        self.oborova_katedra = oborova_katedra

    def __repr__(self):
        return f"Student(Příjmení={self.prijmeni}, Jméno={self.jmeno}, Osobní čís.={self.osobni_cislo}, Název oboru/specializace={self.obor_specializace}, Školitel={self.skolitel}, Oborová katedra={self.oborova_katedra})"

# Convert each row into a Student object
students = []
for _, row in df_filtered.iterrows():
    student = Student(
        prijmeni=row['Příjmení'],
        jmeno=row['Jméno'],
        osobni_cislo=row['Osobní čís.'],
        obor_specializace=row['Název oboru/specializace'],
        skolitel=row['Školitel'],
        oborova_katedra=row['Oborová katedra']
    )
    students.append(student)

# Check the list of student objects
for student in students:
    print(student)

