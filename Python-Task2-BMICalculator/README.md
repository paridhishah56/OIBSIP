# BMI Calculator

## Objective

Calculate Body Mass Index (BMI) from a person's weight in kilograms and height in meters, then display the matching category.

## Requirements

- Python 3
- No third-party packages are required. The tests use Python's built-in `unittest` module.

## Run the program

Open PowerShell in this project folder and run:

```powershell
python .\bmi_calculator.py
```

Enter your weight in kilograms and your height in meters when prompted.

## Sample output

```text
BMI Calculator
Enter your weight in kilograms: 70
Enter your height in meters: 1.75

Your BMI is: 22.86
Category: Normal
```

## BMI categories

- Underweight: BMI < 18.5
- Normal: BMI >= 18.5 and BMI < 25
- Overweight: BMI >= 25 and BMI < 30
- Obese: BMI >= 30

## Input validation

The program accepts numeric weight and height values greater than zero. If an entry is non-numeric, zero, or negative, it displays a clear error and asks again. The BMI is calculated as `weight / (height ** 2)` and displayed to two decimal places.

## Run the tests

Run the built-in tests from this project folder:

```powershell
python -m unittest -v
```

The tests cover BMI calculation, all four categories and their boundaries, invalid values, and retrying after invalid input.