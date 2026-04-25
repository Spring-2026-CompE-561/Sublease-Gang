"use client";

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
import { useRouter } from "next/navigation";

const signupSchema = z
  .object({
    email: z.email("Invalid email address."),
    username: z
      .string()
      .min(3, "Username must be at least 3 characters.")
      .max(32, "Username must be at most 32 characters."),
    password: z
      .string()
      .min(4, "Password must be at least 4 characters.")
      .max(32, "Password must be at most 32 characters."),
    confirmPassword: z.string(),
  })
  .refine((values) => values.password === values.confirmPassword, {
    message: "Passwords do not match.",
    path: ["confirmPassword"],
  });

type SignupValues = z.infer<typeof signupSchema>;

export function SignupForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const form = useForm<SignupValues>({
    resolver: zodResolver(signupSchema),
    defaultValues: {
      email: "",
      username: "",
      password: "",
      confirmPassword: "",
    },
  });
  const router = useRouter();

  async function onSubmit(data: SignupValues) {
    const res = await fetch("http://localhost:8000/api/v1/auth/signup", {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: data.email,
        username: data.username,
        password: data.password,
      }),
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      toast.error("Registration failed: " + (errorData?.detail || "Unknown error"));
      return;
    }

    toast.success("Account created successfully! You can now sign in.");
    router.push("/signin");
  }

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card>
        <CardHeader>
          <CardTitle>Create your SubLease account</CardTitle>
          <CardDescription>
            Add a few details below to get started.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form id="form-signup" onSubmit={form.handleSubmit(onSubmit)}>
            <FieldGroup>
              <Controller
                name="email"
                control={form.control}
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="form-signup-email">Email</FieldLabel>
                    <Input
                      {...field}
                      id="form-signup-email"
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
              <Controller
                name="username"
                control={form.control}
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="form-signup-username">
                      Username
                    </FieldLabel>
                    <Input
                      {...field}
                      id="form-signup-username"
                      aria-invalid={fieldState.invalid}
                      placeholder="yourname"
                      autoComplete="username"
                    />
                    {fieldState.invalid && (
                      <FieldError errors={[fieldState.error]} />
                    )}
                  </Field>
                )}
              />
              <Controller
                name="password"
                control={form.control}
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="form-signup-password">
                      Password
                    </FieldLabel>
                    <Input
                      {...field}
                      id="form-signup-password"
                      aria-invalid={fieldState.invalid}
                      type="password"
                      placeholder="••••••••"
                      autoComplete="new-password"
                    />
                    {fieldState.invalid && (
                      <FieldError errors={[fieldState.error]} />
                    )}
                  </Field>
                )}
              />
              <Controller
                name="confirmPassword"
                control={form.control}
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="form-signup-confirm-password">
                      Confirm password
                    </FieldLabel>
                    <Input
                      {...field}
                      id="form-signup-confirm-password"
                      aria-invalid={fieldState.invalid}
                      type="password"
                      placeholder="••••••••"
                      autoComplete="new-password"
                    />
                    {fieldState.invalid && (
                      <FieldError errors={[fieldState.error]} />
                    )}
                  </Field>
                )}
              />
            </FieldGroup>
          </form>
        </CardContent>
        <CardFooter>
          <div className="flex w-full flex-col gap-4">
            <Field orientation="horizontal">
              <Button
                type="button"
                variant="outline"
                onClick={() => form.reset()}
              >
                Reset
              </Button>
              <Button type="submit" form="form-signup">
                Create account
              </Button>
            </Field>
            <p className="text-sm text-muted-foreground">
              Already have an account?{" "}
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