# Risk Checker

A corporate anti-social risk assesment tool built in Python using SerpApi. Developed from January 2026. The application takes an .xlsx file with a list of client/supplier details
and runs it through a search analysis. The results are then parsed and checked for the appearance of specific keywords that hint connections with anti-social groups or organizations.

Note: This application is primarily intended for Japanese domestic firms and the criteria is also adjusted for that intended use. However, it is possible to alter the keywords to
fit other uses as well.

## Assessment Criteria
Negative keywords can be grouped into 3 levels (高、中、低) according to their risk severity. When a keyword is found in a search result, the application assigns "weights" to the 
result, which is then tallied. The final assessment is made based on the total weights. More weights are placed on sources from trusted domains and other media outlets.
Please note that the mere presence of a high risk keyword in the search result does not mean it gets assessed as "high risk" immediately. Sources commonly associated with 
unverified information, such as personal blogs or forums, are handled as less severe, which could result in a company being assessed as "low risk" while still being associated with
mid or high risk keywords.

## Screenshot
Result output example

<img width="926" height="171" alt="Screenshot (1429)" src="https://github.com/user-attachments/assets/f10d2368-8963-4c11-9645-74afba0c9f36" />

## Installation and How To Use
Simply place your source Excel file in the same directory as the code and run the "main.py" script. Your output file will be created once all operations are completed.

Note: Requires a SerpApi key to function. Please add the key in the .env file before execution.

## License
This project is licensed under the MIT License - see the LICENSE.txt file for details.
