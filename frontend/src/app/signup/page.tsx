"use client";

import { FormEvent, useState } from "react";
import {
  EuiButton,
  EuiCallOut,
  EuiFieldText,
  EuiForm,
  EuiFormRow,
  EuiPanel,
  EuiSpacer,
  EuiText,
  EuiTitle,
} from "@elastic/eui";
import { registerUser } from "@/utils/auth";

type FormValues = {
  username: string;
  email: string;
  password: string;
  firstName: string;
  lastName: string;
};

const initialValues: FormValues = {
  username: "",
  email: "",
  password: "",
  firstName: "",
  lastName: "",
};

export default function SignupPage() {
  const [values, setValues] = useState<FormValues>(initialValues);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fieldErrors = {
    username: values.username.trim() ? undefined : "Username is required.",
    email: values.email.trim() ? undefined : "Email is required.",
    password: values.password ? undefined : "Password is required.",
  };

  const hasClientErrors = Boolean(fieldErrors.username || fieldErrors.email || fieldErrors.password);

  const handleChange =
    (field: keyof FormValues) =>
    (event: React.ChangeEvent<HTMLInputElement>) => {
      setValues((current) => ({ ...current, [field]: event.target.value }));
    };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setSuccessMessage(null);

    if (hasClientErrors) {
      setError("Enter a username, email, and password to continue.");
      return;
    }

    setIsSubmitting(true);

    try {
      const user = await registerUser({
        username: values.username.trim(),
        email: values.email.trim(),
        password: values.password,
        first_name: values.firstName.trim(),
        last_name: values.lastName.trim(),
      });

      setSuccessMessage(`Account created for ${user.username}. Your session is ready.`);
      setValues(initialValues);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div style={{ minHeight: "70vh", display: "flex", alignItems: "center", justifyContent: "center", padding: 24 }}>
      <EuiPanel paddingSize="l" style={{ width: "100%", maxWidth: 520, backgroundColor: "#161616" }}>
        <EuiTitle size="l">
          <h1 style={{ color: "#FFD700" }}>Create account</h1>
        </EuiTitle>
        <EuiSpacer size="s" />
        <EuiText color="subdued">
          <p>Create your GamerHive account and start tracking games.</p>
        </EuiText>
        <EuiSpacer />

        {error && (
          <>
            <EuiCallOut title="Could not create account" color="danger" iconType="error">
              <p>{error}</p>
            </EuiCallOut>
            <EuiSpacer />
          </>
        )}

        {successMessage && (
          <>
            <EuiCallOut title="Account created" color="success" iconType="check">
              <p>{successMessage}</p>
            </EuiCallOut>
            <EuiSpacer />
          </>
        )}

        <EuiForm component="form" onSubmit={handleSubmit}>
          <EuiFormRow label="Username" isInvalid={Boolean(fieldErrors.username)} error={fieldErrors.username}>
            <EuiFieldText
              name="username"
              value={values.username}
              onChange={handleChange("username")}
              isInvalid={Boolean(fieldErrors.username)}
              disabled={isSubmitting}
              autoComplete="username"
            />
          </EuiFormRow>

          <EuiFormRow label="Email" isInvalid={Boolean(fieldErrors.email)} error={fieldErrors.email}>
            <EuiFieldText
              type="email"
              name="email"
              value={values.email}
              onChange={handleChange("email")}
              isInvalid={Boolean(fieldErrors.email)}
              disabled={isSubmitting}
              autoComplete="email"
            />
          </EuiFormRow>

          <EuiFormRow label="Password" isInvalid={Boolean(fieldErrors.password)} error={fieldErrors.password}>
            <input
              type="password"
              name="password"
              value={values.password}
              onChange={handleChange("password")}
              disabled={isSubmitting}
              autoComplete="new-password"
              aria-invalid={Boolean(fieldErrors.password)}
              style={{
                width: "100%",
                padding: "8px 12px",
                borderRadius: 4,
                border: `1px solid ${fieldErrors.password ? "#BD271E" : "#D3DAE6"}`,
                background: isSubmitting ? "#F5F7FA" : "#fff",
                color: "#343741",
              }}
            />
          </EuiFormRow>

          <EuiFormRow label="First name">
            <EuiFieldText
              name="firstName"
              value={values.firstName}
              onChange={handleChange("firstName")}
              disabled={isSubmitting}
              autoComplete="given-name"
            />
          </EuiFormRow>

          <EuiFormRow label="Last name">
            <EuiFieldText
              name="lastName"
              value={values.lastName}
              onChange={handleChange("lastName")}
              disabled={isSubmitting}
              autoComplete="family-name"
            />
          </EuiFormRow>

          <EuiSpacer />
          <EuiButton type="submit" fill isLoading={isSubmitting} disabled={isSubmitting}>
            Create account
          </EuiButton>
        </EuiForm>

      </EuiPanel>
    </div>
  );
}
