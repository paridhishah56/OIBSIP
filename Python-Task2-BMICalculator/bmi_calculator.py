def calculate_bmi(weight, height):
    try:
        weight = float(weight)
    except (TypeError, ValueError) as error:
        raise ValueError("Weight must be a number.") from error

    try:
        height = float(height)
    except (TypeError, ValueError) as error:
        raise ValueError("Height must be a number.") from error

    if weight <= 0:
        raise ValueError("Weight must be greater than zero.")
    if height <= 0:
        raise ValueError("Height must be greater than zero.")

    return weight / (height ** 2)


def classify_bmi(bmi):
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal"
    if bmi < 30:
        return "Overweight"
    return "Obese"


def get_positive_number(prompt, field_name):
    while True:
        user_input = input(prompt)

        try:
            value = float(user_input)
        except ValueError:
            print(f"Error: {field_name} must be a number. Please try again.")
            continue

        if value <= 0:
            print(f"Error: {field_name} must be greater than zero. Please try again.")
            continue

        return value


def main():
    print("BMI Calculator")
    weight = get_positive_number("Enter your weight in kilograms: ", "Weight")
    height = get_positive_number("Enter your height in meters: ", "Height")

    bmi = calculate_bmi(weight, height)
    category = classify_bmi(bmi)

    print(f"\nYour BMI is: {bmi:.2f}")
    print(f"Category: {category}")


if __name__ == "__main__":
    main()