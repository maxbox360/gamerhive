"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
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
import { useAuth } from "@/contexts/AuthContext";
import { loginUser } from "@/utils/auth";

type FormValues = {
  username: string;
  password: string;
};

const initialValues: FormValues = {
  username: "",
  password: "",
};

export default function LoginPage() {
  const router = useRouter();
  const { refreshUser } = useAuth();
  const [values, setValues] = useState<FormValues>(initialValues);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitAttempted, setSubmitAttempted] = useState(false);

  const handleChange =
    (field: keyof FormValues) =>
    (event: React.ChangeEvent<HTMLInputElement>) => {
      setValues((current) => ({ ...current, [field]: event.target.value }));
    };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (isSubmitting) return;
    setSubmitAttempted(true);
    setError(null);

    const fieldErrors = {
      username: values.username.trim() ? undefined : "Username is required.",
      password: values.password ? undefined : "Password is required.",
    };
    const hasClientErrors = Boolean(fieldErrors.username || fieldErrors.password);

    if (hasClientErrors) {
      setError("Enter your username and password to continue.");
      return;
    }

    setIsSubmitting(true);

    try {
      await loginUser({
        username: values.username.trim(),
        password: values.password,
      });
      await refreshUser();
      router.push("/games");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div style={{ minHeight: "70vh", display: "flex", alignItems: "center", justifyContent: "center", padding: 24 }}>
      <EuiPanel paddingSize="l" style={{ width: "100%", maxWidth: 520, backgroundColor: "#161616" }}>
        <EuiTitle size="l">
          <h1 style={{ color: "#FFD700" }}>Login</h1>
        </EuiTitle>
        <EuiSpacer size="s" />
        <EuiText color="subdued">
          <p>Sign in to your GamerHive account.</p>
        </EuiText>
        <EuiSpacer />

        {error && (
          <>
            <EuiCallOut title="Could not log in" color="danger" iconType="error">
              <p>{error}</p>
            </EuiCallOut>
            <EuiSpacer />
          </>
        )}

        <EuiForm component="form" onSubmit={handleSubmit}>
          <EuiFormRow
            label="Username"
            isInvalid={submitAttempted && !values.username.trim()}
            error={submitAttempted && !values.username.trim() ? "Username is required." : undefined}
          >
            <EuiFieldText
              name="username"
              value={values.username}
              onChange={handleChange("username")}
              isInvalid={submitAttempted && !values.username.trim()}
              disabled={isSubmitting}
              autoComplete="username"
            />
          </EuiFormRow>

          <EuiFormRow
            label="Password"
            isInvalid={submitAttempted && !values.password}
            error={submitAttempted && !values.password ? "Password is required." : undefined}
          >
            <input
              type="password"
              name="password"
              value={values.password}
              onChange={handleChange("password")}
              disabled={isSubmitting}
              autoComplete="current-password"
              aria-invalid={submitAttempted && !values.password}
              style={{
                width: "100%",
                padding: "8px 12px",
                borderRadius: 4,
                border: `1px solid ${submitAttempted && !values.password ? "#BD271E" : "#D3DAE6"}`,
                background: isSubmitting ? "#F5F7FA" : "#fff",
                color: "#343741",
              }}
            />
          </EuiFormRow>

          <EuiSpacer />
          <EuiButton type="submit" fill isLoading={isSubmitting} disabled={isSubmitting}>
            Login
          </EuiButton>
        </EuiForm>

        <EuiSpacer />
        <EuiText size="s" color="subdued">
          <p>
            Need an account? <Link href="/signup">Create one at /signup</Link>.
          </p>
        </EuiText>
      </EuiPanel>
    </div>
  );
}
