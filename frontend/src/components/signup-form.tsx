"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Field,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { HugeiconsIcon } from "@hugeicons/react";
import { CheckmarkCircle02Icon } from "@hugeicons/core-free-icons";
import { cn } from "@/lib/utils";
import { useRouter } from "next/navigation";
import { API_BASE_URL, readApiErrorMessage } from "@/lib/api";
import { saveTokens } from "@/lib/auth";

const NAME_REGEX = /^[A-Za-z\s\-']+$/;
const USERNAME_REGEX = /^\w{3,30}$/;
const PHONE_STRIP_REGEX = /[\s\-()+]/g;

const signupSchema = z
  .object({
    firstname: z
      .string()
      .min(1, "First name is required.")
      .max(50, "First name must be at most 50 characters.")
      .regex(NAME_REGEX, "Must contain only letters, spaces, or hyphens."),
    lastname: z
      .string()
      .min(1, "Last name is required.")
      .max(50, "Last name must be at most 50 characters.")
      .regex(NAME_REGEX, "Must contain only letters, spaces, or hyphens."),
    email: z.email("Invalid email address."),
    username: z
      .string()
      .regex(
        USERNAME_REGEX,
        "Must be 3-30 characters, letters/numbers/underscores only.",
      ),
    password: z
      .string()
      .min(12, "Password must be at least 12 characters.")
      .max(128, "Password must be at most 128 characters."),
    confirmPassword: z.string(),
    contact_email: z
      .union([z.literal(""), z.email("Invalid contact email.")])
      .optional(),
    contact_phone: z
      .string()
      .max(20, "Phone must be at most 20 characters.")
      .optional()
      .refine(
        (value) => {
          if (!value) return true;
          const digits = value.replace(PHONE_STRIP_REGEX, "");
          return /^\d+$/.test(digits) && digits.length >= 7 && digits.length <= 15;
        },
        { message: "Must be a valid phone number (7-15 digits)." },
      ),
    description: z
      .string()
      .max(500, "Bio must be at most 500 characters.")
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
      description: "",
    },
  });
  const router = useRouter();

  const [iconFile, setIconFile] = useState<File | null>(null);
  const [iconPreview, setIconPreview] = useState<string | null>(null);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [pendingValues, setPendingValues] = useState<SignupValues | null>(null);
  const [phase, setPhase] = useState<"confirm" | "submitting" | "success">(
    "confirm",
  );
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const dialogBusy = phase !== "confirm";

  const firstnameValue = form.watch("firstname");
  const initials = firstnameValue
    ? firstnameValue.charAt(0).toUpperCase()
    : "?";

  useEffect(() => {
    if (!iconFile) {
      setIconPreview(null);
      return;
    }
    const url = URL.createObjectURL(iconFile);
    setIconPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [iconFile]);

  function handleIconChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0] ?? null;
    if (file && file.type !== "image/png" && file.type !== "image/jpeg") {
      toast.error("Profile photo must be a PNG or JPEG image.");
      event.target.value = "";
      return;
    }
    setIconFile(file);
  }

  function handleReset() {
    form.reset();
    setIconFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  function handleRequestConfirm(data: SignupValues) {
    setPendingValues(data);
    setPhase("confirm");
    setConfirmOpen(true);
  }

  async function handleConfirmCreate() {
    if (!pendingValues) return;
    setPhase("submitting");
    await onSubmit(pendingValues);
  }

  async function onSubmit(data: SignupValues) {
    let res: Response;
    try {
      res = await fetch(`${API_BASE_URL}/api/v1/auth/signup`, {
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
          description: data.description || undefined,
        }),
      });
    } catch {
      toast.error("Could not reach the server. Please try again.");
      setPhase("confirm");
      return;
    }

    if (!res.ok) {
      const message = await readApiErrorMessage(res);
      toast.error(`Registration failed: ${message ?? "Unknown error"}`);
      setPhase("confirm");
      return;
    }

    const tokens = (await res.json()) as {
      access_token?: string;
      refresh_token?: string;
    };
    if (!tokens.access_token) {
      toast.success("Account created. Please sign in to continue.");
      setPhase("success");
      await new Promise((resolve) => setTimeout(resolve, 1500));
      router.push("/signin");
      return;
    }

    saveTokens({
      access_token: tokens.access_token,
      refresh_token: tokens.refresh_token,
    });

    if (iconFile) {
      const formData = new FormData();
      formData.append("file", iconFile);
      try {
        const iconRes = await fetch(
          `${API_BASE_URL}/api/v1/profiles/me/icon`,
          {
            method: "POST",
            headers: { Authorization: `Bearer ${tokens.access_token}` },
            body: formData,
          },
        );
        if (!iconRes.ok) {
          toast.warning("Account created, but profile photo upload failed.");
        }
      } catch {
        toast.warning("Account created, but profile photo upload failed.");
      }
    }

    toast.success("Welcome to SubLease!");
    setPhase("success");
    await new Promise((resolve) => setTimeout(resolve, 1800));
    router.push("/");
    router.refresh();
  }

  return (
    <>
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card>
        <CardHeader>
          <CardTitle>Create your SubLease account</CardTitle>
          <CardDescription>
            Add a few details below to get started.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form id="form-signup" onSubmit={form.handleSubmit(handleRequestConfirm)}>
            <FieldGroup>
              <div className="flex items-center gap-6">
                <div className="flex shrink-0 flex-col items-center gap-2">
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="rounded-full focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                    aria-label="Upload profile picture"
                  >
                    <Avatar className="size-24">
                      {iconPreview ? <AvatarImage src={iconPreview} /> : null}
                      <AvatarFallback className="text-2xl">
                        {initials}
                      </AvatarFallback>
                    </Avatar>
                  </button>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    {iconFile ? "Change photo" : "Upload photo"}
                  </Button>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/png,image/jpeg"
                    onChange={handleIconChange}
                    className="hidden"
                  />
                </div>
                <div className="flex flex-1 flex-col gap-7">
                  <Controller
                    name="firstname"
                    control={form.control}
                    render={({ field, fieldState }) => (
                      <Field data-invalid={fieldState.invalid}>
                        <FieldLabel htmlFor="form-signup-firstname">
                          First name{" "}
                          <span aria-hidden="true" className="text-destructive">
                            *
                          </span>
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
                          Last name{" "}
                          <span aria-hidden="true" className="text-destructive">
                            *
                          </span>
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
              </div>
              <div className="grid grid-cols-1 gap-7 sm:grid-cols-2 sm:gap-4">
                <Controller
                  name="email"
                  control={form.control}
                  render={({ field, fieldState }) => (
                    <Field data-invalid={fieldState.invalid}>
                      <FieldLabel htmlFor="form-signup-email">
                        Email{" "}
                        <span aria-hidden="true" className="text-destructive">
                          *
                        </span>
                      </FieldLabel>
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
                        Username{" "}
                        <span aria-hidden="true" className="text-destructive">
                          *
                        </span>
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
                        Password{" "}
                        <span aria-hidden="true" className="text-destructive">
                          *
                        </span>
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
                        Confirm password{" "}
                        <span aria-hidden="true" className="text-destructive">
                          *
                        </span>
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
              <Controller
                name="description"
                control={form.control}
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="form-signup-description">
                      About you{" "}
                      <span className="text-muted-foreground font-normal">
                        (optional)
                      </span>
                    </FieldLabel>
                    <Textarea
                      {...field}
                      id="form-signup-description"
                      aria-invalid={fieldState.invalid}
                      placeholder="Tell others a bit about yourself..."
                      maxLength={500}
                      rows={4}
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
                onClick={handleReset}
                disabled={form.formState.isSubmitting}
              >
                Reset
              </Button>
              <Button
                type="submit"
                form="form-signup"
                disabled={form.formState.isSubmitting}
              >
                {form.formState.isSubmitting ? "Creating account…" : "Create account"}
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
    <Dialog
      open={confirmOpen}
      onOpenChange={(open) => {
        if (dialogBusy) return;
        setConfirmOpen(open);
      }}
    >
      <DialogContent showCloseButton={phase === "confirm"}>
        {phase === "confirm" && (
          <>
            <DialogHeader>
              <DialogTitle>Before you create your account</DialogTitle>
              <DialogDescription>
                To create your SubLease account, we collect personal
                information including your name, email, and (if you provide
                it) a contact phone number. By continuing you agree to our{" "}
                <Link href="/terms" target="_blank" rel="noopener noreferrer">
                  Terms of Service
                </Link>{" "}
                and acknowledge our{" "}
                <Link
                  href="/privacy"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Privacy Policy
                </Link>
                , which describe how your information is used and stored.
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setConfirmOpen(false)}
              >
                Cancel
              </Button>
              <Button type="button" onClick={handleConfirmCreate}>
                I agree, create account
              </Button>
            </DialogFooter>
          </>
        )}
        {phase === "submitting" && (
          <div
            role="status"
            aria-live="polite"
            className="flex flex-col items-center gap-3 py-6 text-center"
          >
            <div className="h-8 w-8 animate-spin rounded-full border-2 border-muted-foreground border-t-transparent" />
            <DialogTitle>Creating your account…</DialogTitle>
            <DialogDescription>
              Hang tight while we set things up.
            </DialogDescription>
          </div>
        )}
        {phase === "success" && (
          <div
            role="status"
            aria-live="polite"
            className="flex flex-col items-center gap-3 py-6 text-center"
          >
            <HugeiconsIcon
              icon={CheckmarkCircle02Icon}
              className="h-10 w-10 text-emerald-500"
              strokeWidth={2}
            />
            <DialogTitle>Account created!</DialogTitle>
            <DialogDescription>
              Welcome to SubLease. Redirecting you now…
            </DialogDescription>
            <div className="mt-1 h-5 w-5 animate-spin rounded-full border-2 border-muted-foreground border-t-transparent" />
          </div>
        )}
      </DialogContent>
    </Dialog>
    </>
  );
}