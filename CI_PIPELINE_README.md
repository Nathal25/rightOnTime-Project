# CI/CD Pipeline with SonarCloud

## 🎯 Overview

This project includes a complete CI/CD pipeline with **SonarCloud** integration to ensure code quality and maintainability. The pipeline automatically runs on every push and pull request.

## 📊 Metrics Measured

### 1. **Cyclomatic Complexity**
- **What it measures**: The number of independent paths through the code
- **Threshold**: 15 per function
- **Why it matters**: High complexity makes code harder to understand, test, and maintain

### 2. **Code Coverage**
- **What it measures**: Percentage of code executed by tests
- **Target**: 60% minimum
- **Why it matters**: Higher coverage means more code is tested, reducing bugs

### 3. **Code Duplication**
- **What it measures**: Duplicate code blocks across the project
- **Threshold**: Minimum 50 tokens
- **Why it matters**: Duplication increases maintenance costs and bug risk

### 4. **Technical Debt**
- **What it measures**: Estimated time to fix all code quality issues
- **Calculation**: Based on issue severity and quantity
- **Why it matters**: Helps prioritize refactoring efforts

### 5. **Code Smells**
- **What it measures**: Maintainability issues in code structure
- **Examples**: Long methods, too many parameters, complex conditions
- **Why it matters**: Indicates areas that need refactoring

## 🚀 Pipeline Stages

### Stage 1: Test & Coverage
```yaml
- Checkout code
- Setup Python 3.11
- Install dependencies
- Run Django tests with coverage
- Generate coverage report (XML format)
- Upload coverage artifacts
```

### Stage 2: SonarCloud Analysis
```yaml
- Checkout code
- Setup Python 3.11
- Install dependencies
- Run tests with coverage
- Download coverage reports
- Execute SonarCloud scan
- Analyze metrics and quality
```

### Stage 3: Quality Gate
```yaml
- Verify Quality Gate status
- Check if code meets quality standards
- Fail pipeline if standards not met
```

## 📁 Configuration Files

| File | Purpose |
|------|---------|
| `.github/workflows/ci.yml` | GitHub Actions pipeline configuration |
| `sonar-project.properties` | SonarCloud project settings and metrics |
| `.coveragerc` | Python coverage tool configuration |
| `pytest.ini` | Pytest testing framework settings |
| `SONARCLOUD_SETUP.md` | Detailed setup instructions |

## 🔧 Setup Instructions

### Quick Start

1. **Create SonarCloud Account**
   - Go to [sonarcloud.io](https://sonarcloud.io)
   - Sign in with GitHub
   - Import your repository

2. **Add GitHub Secret**
   - Repository Settings → Secrets → Actions
   - Add `SONAR_TOKEN` (from SonarCloud)

3. **Push Code**
   ```bash
   git push origin nog
   ```

4. **View Results**
   - Check GitHub Actions tab
   - Visit SonarCloud dashboard

For detailed instructions, see [SONARCLOUD_SETUP.md](./SONARCLOUD_SETUP.md)

## 📈 Quality Standards

### Default Quality Gate Criteria
- ✅ Coverage on new code > 80%
- ✅ Duplicated lines < 3%
- ✅ Maintainability Rating = A
- ✅ Reliability Rating = A
- ✅ Security Rating = A
- ✅ Security Hotspots Reviewed = 100%

### Project-Specific Standards
- Cyclomatic complexity < 15 per function
- Minimum code coverage: 60%
- Code duplication: Monitored per commit

## 🧪 Running Tests Locally

### Run All Tests
```bash
cd rightOnTime
python manage.py test
```

### Run Tests with Coverage
```bash
coverage run --source='.' manage.py test
coverage report
coverage html  # View in browser: htmlcov/index.html
```

### Run with Pytest
```bash
pytest --cov=rightOnTime --cov-report=html
```

## 📊 Viewing Results

### GitHub Actions
1. Go to repository → **Actions** tab
2. Click on latest workflow run
3. View job details and logs
4. Check SonarCloud summary

### SonarCloud Dashboard
1. Visit [sonarcloud.io](https://sonarcloud.io)
2. Select your project
3. View metrics in **Overview** tab
4. Explore issues in **Issues** tab
5. Check code coverage in **Measures** tab

## 🔍 Understanding the Reports

### Overview Tab (SonarCloud)
- **Bugs**: Logic errors that can cause failures
- **Vulnerabilities**: Security issues
- **Code Smells**: Maintainability problems
- **Coverage**: Test coverage percentage
- **Duplications**: Percentage of duplicated code
- **Technical Debt**: Time to fix all issues

### Issues Tab (SonarCloud)
- Filter by: Type, Severity, Status
- See specific code locations
- Get fix recommendations
- Track issue history

### Measures Tab (SonarCloud)
- Detailed metrics breakdown
- Historical trends
- Complexity distribution
- File-level metrics

## 🛠️ Customization

### Adjust Coverage Threshold
Edit `.coveragerc`:
```ini
[report]
fail_under = 70  # Change from 60 to 70
```

### Modify Complexity Threshold
Edit `sonar-project.properties`:
```properties
sonar.python.cyclomaticComplexity.threshold=20
```

### Exclude Files from Analysis
Edit `sonar-project.properties`:
```properties
sonar.exclusions=**/migrations/**,**/custom_folder/**
```

### Change Quality Gate
1. Go to SonarCloud dashboard
2. Project Settings → Quality Gates
3. Select or create custom gate
4. Set your own thresholds

## 🐛 Troubleshooting

### Pipeline Fails: "No SONAR_TOKEN"
**Solution**: Add `SONAR_TOKEN` to GitHub Secrets

### Coverage Report Not Found
**Solution**: Ensure tests run successfully before SonarCloud analysis

### Quality Gate Fails
**Solution**: 
1. Check SonarCloud dashboard for specific issues
2. Fix code quality problems
3. Push changes to re-run pipeline

### Tests Fail in CI but Pass Locally
**Solution**: 
1. Check environment variables
2. Verify database configuration
3. Review SECRET_KEY settings

## 📚 Resources

- [SonarCloud Documentation](https://docs.sonarcloud.io/)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/)
- [Coverage.py Docs](https://coverage.readthedocs.io/)

## 🎓 Best Practices

1. **Write Tests First**: Aim for >80% coverage on new code
2. **Keep Functions Small**: Target complexity < 10
3. **Review SonarCloud**: Check dashboard after each push
4. **Fix Issues Early**: Address code smells before they accumulate
5. **Monitor Trends**: Watch technical debt over time

## 🤝 Contributing

When contributing:
1. Ensure all tests pass
2. Maintain or improve code coverage
3. Keep cyclomatic complexity low
4. Fix any new code smells
5. Check SonarCloud quality gate passes

## 📝 License

This pipeline configuration is part of the RightOnTime project.

---

**Last Updated**: November 2025  
**Pipeline Version**: 1.0  
**SonarCloud Integration**: Active
