"use client";

import { useState } from "react";
import Link from "next/link";
import { z } from "zod";
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Field,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

const formSchema = z.object({
  email: z.email("Invalid email address."),
});

type ForgotPasswordValues = z.infer<typeof formSchema>;

export function ForgotPasswordForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const [submitted, setSubmitted] = useState(false);
  const form = useForm<ForgotPasswordValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { email: "" },
  });

  async function onSubmit(data: ForgotPasswordValues) {
    const res = await fetch("http://localhost:8000/api/v1/auth/forgot_password", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email: data.email }),
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      toast.error("Request failed: " + (errorData?.detail || "Unknown error"));
      return;
    }

    setSubmitted(true);
    toast.success("If that email is registered, a reset link has been sent.");
  }

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card>
        <CardHeader>
          <CardTitle>Forgot your password?</CardTitle>
          <CardDescription>
            Enter your email and we&apos;ll send you a link to reset your password.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {submitted ? (
            <p className="text-sm text-muted-foreground">
              If an account with that email exists, a reset link has been sent. Check your inbox.
            </p>
          ) : (
            <form id="form-forgot-password" onSubmit={form.handleSubmit(onSubmit)}>
              <FieldGroup>
                <Controller
                  name="email"
                  control={form.control}
                  render={({ field, fieldState }) => (
                    <Field data-invalid={fieldState.invalid}>
                      <FieldLabel htmlFor="form-forgot-email">Email</FieldLabel>
                      <Input
                        {...field}
                        id="form-forgot-email"
                        aria-invalid={fieldState.invalid}
                        placeholder="you@example.com"
                        autoComplete="email"
                      />
                      {fieldState.invalid && (
                        <FieldError errors={[fieldState.error]} />
                      )}
                    </Field>
                  )}
                />
              </FieldGroup>
            </form>
          )}
        </CardContent>
        <CardFooter>
          <div className="flex w-full flex-col gap-4">
            {!submitted && (
              <Button type="submit" form="form-forgot-password">
                Send reset link
              </Button>
            )}
            <p className="text-sm text-muted-foreground">
              Remember your password?{" "}
              <Link
                href="/signin"
                className="font-medium text-foreground underline underline-offset-4"
              >
                Sign in
              </Link>
              .
            </p>
          </div>
        </CardFooter>
      </Card>
    </div>
  );
}