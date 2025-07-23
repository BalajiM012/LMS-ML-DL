# Deployment and Local Development Guide

## Running Backend Locally

1. Ensure you have Python and required dependencies installed.
2. Run the Flask backend server:
   ```bash
   python app.py
   ```
   By default, the backend will run on `http://localhost:5000`.

## Running Frontend Locally

1. Install Node.js dependencies:
   ```bash
   npm install
   ```
2. Run the Next.js frontend development server:
   ```bash
   npm run dev
   ```
3. The frontend will run on `http://localhost:3000`.

### Connecting Frontend to Backend Locally

- The frontend fetch calls to backend API use the environment variable `BACKEND_URL`.
- For local development, ensure `BACKEND_URL` is set to `http://localhost:5000`.
- You can set this in your shell before running the frontend:
  ```bash
  export BACKEND_URL=http://localhost:5000
  ```
- Alternatively, the frontend fetch calls default to `http://localhost:5000` if `BACKEND_URL` is not set.

## Deploying Frontend to Netlify

1. Push your frontend code to a GitHub repository.
2. Connect your GitHub repository to Netlify.
3. In Netlify dashboard, set the following build environment variable:
   - `BACKEND_URL` = your backend API URL (e.g., `https://your-backend-domain.com`)
4. Netlify will use the `netlify.toml` configuration to build and deploy the frontend.
5. The `/api/*` requests will be proxied to the backend URL as configured.

## Pushing Code to GitHub

1. Initialize git (if not already done):
   ```bash
   git init
   ```
2. Add your remote repository:
   ```bash
   git remote add origin git@github.com:MBALAJIMtech/LMS---Library-Management-System-website.git
   ```
   *(If the remote already exists, update it with: `git remote set-url origin git@github.com:MBALAJIMtech/LMS---Library-Management-System-website.git`)*
3. Stage and commit your changes:
   ```bash
   git add .
   git commit -m "Your commit message"
   ```
4. Push to GitHub:
   ```bash
   git push -u origin main
   ```

> **Note:**  
> If you see a `Permission denied (publickey)` error, ensure your SSH key is added to your GitHub account. See [GitHub SSH setup instructions](https://docs.github.com/en/authentication/connecting-to-github-with-ssh).

## Notes

- Ensure CORS is properly configured on your backend to allow requests from your frontend domain.
- For production, update the `BACKEND_URL` environment variable accordingly.
