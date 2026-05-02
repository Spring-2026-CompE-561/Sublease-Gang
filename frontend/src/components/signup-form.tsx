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
import { API_BASE_URL, readApiErrorMessage } from "@/lib/api";

const signupSchema = z
  .object({
    firstname: z
      .string()
      .min(1, "First name is required.")
      .max(50, "First name must be at most 50 characters."),
    lastname: z
      .string()
      .min(1, "Last name is required.")
      .max(50, "Last name must be at most 50 characters."),
    email: z.email("Invalid email address."),
    username: z
      .string()
      .min(3, "Username must be at least 3 characters.")
      .max(32, "Username must be at most 32 characters."),
    password: z
      .string()
      .min(8, "Password must be at least 8 characters.")
      .max(32, "Password must be at most 32 characters."),
    confirmPassword: z.string(),
    contact_email: z
      .union([z.literal(""), z.email("Invalid contact email.")])
      .optional(),
    contact_phone: z
      .string()
      .max(20, "Phone must be at most 20 characters.")
      .optional(),
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
      firstname: "",
      lastname: "",
      email: "",
      username: "",
      password: "",
      confirmPassword: "",
      contact_email: "",
      contact_phone: "",
    },
  });
  const router = useRouter();

  async function onSubmit(data: SignupValues) {
    const res = await fetch(`${API_BASE_URL}/api/v1/auth/signup`, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        email: data.email,
        username: data.username,
        password: data.password,
        firstname: data.firstname,
        lastname: data.lastname,
        contact_email: data.contact_email || undefined,
        contact_phone: data.contact_phone || undefined,
      }),
    });

    if (!res.ok) {
      const message = await readApiErrorMessage(res);
      toast.error(`Registration failed: ${message ?? "Unknown error"}`);
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
              <div className="grid grid-cols-1 gap-7 sm:grid-cols-2 sm:gap-4">
                <Controller
                  name="firstname"
                  control={form.control}
                  render={({ field, fieldState }) => (
                    <Field data-invalid={fieldState.invalid}>
                      <FieldLabel htmlFor="form-signup-firstname">
                        First name
                      </FieldLabel>
                      <Input
                        {...field}
                        id="form-signup-firstname"
                        aria-invalid={fieldState.invalid}
                        placeholder="Jane"
                        autoComplete="given-name"
                        maxLength={50}
                      />
                      {fieldState.invalid && (
                        <FieldError errors={[fieldState.error]} />
                      )}
                    </Field>
                  )}
                />
                <Controller
                  name="lastname"
                  control={form.control}
                  render={({ field, fieldState }) => (
                    <Field data-invalid={fieldState.invalid}>
                      <FieldLabel htmlFor="form-signup-lastname">
                        Last name
                      </FieldLabel>
                      <Input
                        {...field}
                        id="form-signup-lastname"
                        aria-invalid={fieldState.invalid}
                        placeholder="Doe"
                        autoComplete="family-name"
                        maxLength={50}
                      />
                      {fieldState.invalid && (
                        <FieldError errors={[fieldState.error]} />
                      )}
                    </Field>
                  )}
                />
              </div>
              <div className="grid grid-cols-1 gap-7 sm:grid-cols-2 sm:gap-4">
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
              </div>
              <div className="grid grid-cols-1 gap-7 sm:grid-cols-2 sm:gap-4">
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
              </div>
              <div className="grid grid-cols-1 gap-7 sm:grid-cols-2 sm:gap-4">
                <Controller
                  name="contact_email"
                  control={form.control}
                  render={({ field, fieldState }) => (
                    <Field data-invalid={fieldState.invalid}>
                      <FieldLabel htmlFor="form-signup-contact-email">
                        Contact email{" "}
                        <span className="text-muted-foreground font-normal">
                          (optional)
                        </span>
                      </FieldLabel>
                      <Input
                        {...field}
                        id="form-signup-contact-email"
                        aria-invalid={fieldState.invalid}
                        type="email"
                        placeholder="contact@example.com"
                        autoComplete="email"
                        maxLength={254}
                      />
                      {fieldState.invalid && (
                        <FieldError errors={[fieldState.error]} />
                      )}
                    </Field>
                  )}
                />
                <Controller
                  name="contact_phone"
                  control={form.control}
                  render={({ field, fieldState }) => (
                    <Field data-invalid={fieldState.invalid}>
                      <FieldLabel htmlFor="form-signup-contact-phone">
                        Contact phone{" "}
                        <span className="text-muted-foreground font-normal">
                          (optional)
                        </span>
                      </FieldLabel>
                      <Input
                        {...field}
                        id="form-signup-contact-phone"
                        aria-invalid={fieldState.invalid}
                        type="tel"
                        placeholder="+1 (555) 555-5555"
                        autoComplete="tel"
                        maxLength={20}
                      />
                      {fieldState.invalid && (
                        <FieldError errors={[fieldState.error]} />
                      )}
                    </Field>
                  )}
                />
              </div>
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