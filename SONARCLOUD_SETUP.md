# SonarCloud Setup Guide for RightOnTime Project

## Overview
This guide will help you configure SonarCloud for your Django project to measure code quality metrics including:
- **Cyclomatic Complexity**: Measures code complexity
- **Code Coverage**: Percentage of code covered by tests
- **Code Duplication**: Identifies duplicate code blocks
- **Technical Debt**: Estimated time to fix all issues
- **Code Smells**: Maintainability issues

## Prerequisites
1. GitHub repository: `Nathal25/rightOnTime-Project`
2. SonarCloud account (free for public repositories)

## Setup Steps

### 1. Create SonarCloud Account
1. Go to [SonarCloud](https://sonarcloud.io/)
2. Click "Log in" and sign in with your GitHub account
3. Authorize SonarCloud to access your GitHub repositories

### 2. Import Your Project
1. In SonarCloud, click the **"+"** button in the top right
2. Select **"Analyze new project"**
3. Choose your organization or create a new one (use `nathal25` as suggested)
4. Select the `rightOnTime-Project` repository
5. Click **"Set Up"**

### 3. Configure Project Settings
1. Choose **"With GitHub Actions"** as the analysis method
2. SonarCloud will display your project key and organization
3. Verify they match:
   - **Organization**: `nathal25`
   - **Project Key**: `Nathal25_rightOnTime-Project`

### 4. Add GitHub Secrets
1. Go to your GitHub repository settings
2. Navigate to **Settings > Secrets and variables > Actions**
3. Click **"New repository secret"**
4. Add the following secret:
   - **Name**: `SONAR_TOKEN`
   - **Value**: Copy from SonarCloud (in the setup wizard)

### 5. Update Configuration (if needed)
If your SonarCloud organization or project key is different, update these files:

**`.github/workflows/ci.yml`**:
```yaml
-Dsonar.projectKey=YOUR_PROJECT_KEY
-Dsonar.organization=YOUR_ORGANIZATION
```

**`sonar-project.properties`**:
```properties
sonar.projectKey=YOUR_PROJECT_KEY
sonar.organization=YOUR_ORGANIZATION
```

### 6. Push Changes and Trigger Pipeline
```bash
git add .
git commit -m "Add SonarCloud integration to CI pipeline"
git push origin nog
```

## Metrics Monitored

### 1. **Cyclomatic Complexity**
- Threshold set to 15 per function
- Measures the number of linearly independent paths through code
- Lower is better (simpler code)

### 2. **Code Coverage**
- Target: 60% minimum (configured in `.coveragerc`)
- Measures percentage of code executed by tests
- Generated using Python's `coverage` tool

### 3. **Code Duplication**
- Minimum token threshold: 50
- Identifies copy-pasted code blocks
- Helps maintain DRY (Don't Repeat Yourself) principle

### 4. **Technical Debt**
- Estimated time to fix all code issues
- Development cost: 30 minutes per issue
- Rating grid: A (0-5%), B (5-10%), C (10-20%), D (20-50%), E (>50%)

### 5. **Code Smells**
- Maintainability issues that make code harder to change
- Includes issues like:
  - Long methods/functions
  - Too many parameters
  - Complex conditionals
  - Unused variables

## Quality Gate Criteria

The default Quality Gate checks:
- ✅ Code Coverage on new code > 80%
- ✅ Duplicated Lines on new code < 3%
- ✅ Maintainability Rating = A
- ✅ Reliability Rating = A
- ✅ Security Rating = A
- ✅ Security Hotspots Reviewed = 100%

## Viewing Results

### In SonarCloud Dashboard:
1. Go to [sonarcloud.io](https://sonarcloud.io)
2. Select your project
3. View the **Overview** tab for key metrics
4. Explore **Issues**, **Measures**, and **Code** tabs for details

### In GitHub Actions:
1. Go to your repository's **Actions** tab
2. Select a workflow run
3. View the SonarCloud analysis results
4. Click the SonarCloud link in the workflow summary

## Troubleshooting

### Issue: "No token provided"
**Solution**: Ensure `SONAR_TOKEN` is added to GitHub Secrets

### Issue: "Project not found"
**Solution**: Verify `sonar.projectKey` and `sonar.organization` match your SonarCloud project

### Issue: "Quality Gate failed"
**Solution**: Check the SonarCloud dashboard for specific issues and fix them

### Issue: "Coverage report not found"
**Solution**: Ensure tests are running successfully and generating `coverage.xml`

## Local Testing

To run tests with coverage locally:

```bash
cd rightOnTime
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report in htmlcov/
```

## Additional Resources

- [SonarCloud Documentation](https://docs.sonarcloud.io/)
- [Python Coverage Documentation](https://coverage.readthedocs.io/)
- [Django Testing Documentation](https://docs.djangoproject.com/en/stable/topics/testing/)

## Maintenance

### Update Exclusions
Edit `sonar-project.properties` to exclude specific files/patterns:
```properties
sonar.exclusions=**/migrations/**,**/tests.py
```

### Adjust Quality Standards
Modify thresholds in `sonar-project.properties`:
```properties
sonar.python.cyclomaticComplexity.threshold=15
```

Update coverage minimum in `.coveragerc`:
```ini
fail_under = 60
```

## Support

For issues specific to:
- **SonarCloud**: Check [SonarCloud Community](https://community.sonarsource.com/)
- **GitHub Actions**: Check [GitHub Actions Documentation](https://docs.github.com/en/actions)
- **Project Issues**: Open an issue in your repository
