# AI Usage Documentation

## AI Usage in This Project

### AI Tools Used
- **GitHub Copilot / Cascade**: Used for code generation, refactoring, and documentation
- **ChatGPT**: Used for architectural guidance and problem-solving

### What Was AI-Assisted

1. **Code Structure and Architecture**
   - Initial project structure setup
   - Module organization (pages/, utils/, assets/)
   - Session state management patterns

2. **Data Transformation Functions**
   - Implementation of cleaning functions (utils/data_transformations.py)
   - Outlier detection algorithms (IQR, Z-score)
   - Scaling implementations (Min-Max, Z-Score)

3. **UI Components**
   - CSS styling with dark/light theme variables
   - Navigation structure with session-based routing
   - Chart generation with matplotlib

4. **Documentation**
   - README.md structure and content
   - This AI_USAGE.md file

### What Was Verified Manually

1. **All transformations tested with sample data**
   - Missing value imputation verified with ecommerce_sales.csv
   - Outlier detection tested with hr_employees.csv bonus column
   - Categorical mapping tested with actual category values

2. **UI/UX verification**
   - Tested theme toggle persistence across all pages
   - Verified navigation doesn't open new tabs
   - Checked all buttons and inputs function correctly

3. **Data export functionality**
   - CSV export tested and verified
   - Excel export tested and verified
   - JSON recipe format validated

4. **Sample datasets**
   - Verified 1000+ rows in each dataset
   - Confirmed 8+ columns with mixed types
   - Verified missing values and duplicates present

5. **Requirements validation**
   - All 6 chart types tested and working
   - All 4 pages implemented with required features
   - Transformation log working with undo

### AI Assistance Level

Approximately 70% of the code was AI-generated with manual review and modification. The remaining 30% was manual implementation including:
- Debugging and fixing edge cases
- Testing with actual data
- UI refinement and polish
- Verification of coursework requirements

### Limitations and Known Issues

1. **Calculated columns** use pandas eval() which has limitations on complex expressions
2. **Excel export** creates a temporary file in the working directory
3. **Large datasets** (>50MB) may cause performance issues in browser

### Best Practices Followed

- AI-generated code was always reviewed before use
- All functions include docstrings
- Error handling added to all user inputs
- Session state properly initialized with defaults
- No hardcoded secrets or API keys
