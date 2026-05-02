"use client";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
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
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm, Controller } from "react-hook-form";
import { toast } from "sonner";
import { useRouter } from "next/navigation";

// TODO: lat/lng should come from a map picker. hardcoded for now
const DEFAULT_LAT = 0;
const DEFAULT_LNG = 0;

const formSchema = z.object({
  title: z.string().min(3, "title is too short"),
  description: z.string().min(10, "Need a longer description"),
  price: z.string().min(1, "Price is required."),
  location: z.string().min(2, "Where is it?"),
  room_type: z.string().optional(),
  sqft: z.string().optional(),
  start_date: z.string().min(1, "Pick a start date"),
  end_date: z.string().min(1, "Pick an end date"),
});

type FormValues = z.infer<typeof formSchema>;

export function ListingForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const router = useRouter();
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      title: "",
      description: "",
      price: "",
      location: "",
      room_type: "",
      sqft: "",
      start_date: "",
      end_date: "",
    },
  });

  async function onSubmit(data: FormValues) {
    const price = Number(data.price);
    if (isNaN(price) || price <= 0) {
      toast.error("price must be a number > 0");
      return;
    }

    // make sure the dates make sense
    if (new Date(data.end_date) <= new Date(data.start_date)) {
      toast.error("End date must be after start date");
      return;
    }

    const token = localStorage.getItem("access_token");
    if (!token) {
      toast.error("You need to sign in first");
      router.push("/signin");
      return;
    }

    const payload = {
      title: data.title.trim(),
      description: data.description,
      price,
      location: data.location,
      room_type: data.room_type || null,
      sqft: data.sqft ? Number(data.sqft) : null,
      start_date: new Date(data.start_date).toISOString(),
      end_date: new Date(data.end_date).toISOString(),
      latitude: DEFAULT_LAT,
      longitude: DEFAULT_LNG,
    };

    // console.log(payload);

    try {
      const res = await fetch("http://localhost:8000/api/v1/listings/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        toast.error("Could not post listing: " + (err?.detail || res.statusText));
        return;
      }

      toast.success("Listing posted");
      router.push("/");
      router.refresh();
    } catch (e) {
      console.log("listing post failed", e);
      toast.error("Something went wrong, try again");
    }
  }

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <Card>
        <CardHeader>
          <CardTitle>Post a sublease</CardTitle>
        </CardHeader>
        <CardContent>
          <form id="form-listing" onSubmit={form.handleSubmit(onSubmit)}>
            <FieldGroup>
              <Controller
                name="title"
                control={form.control}
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="form-listing-title">Title</FieldLabel>
                    <Input
                      {...field}
                      id="form-listing-title"
                      aria-invalid={fieldState.invalid}
                      placeholder="Sunny 1BR near campus"
                    />
                    {fieldState.invalid && (
                      <FieldError errors={[fieldState.error]} />
                    )}
                  </Field>
                )}
              />

              <Controller
                name="description"
                control={form.control}
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="form-listing-description">
                      Description
                    </FieldLabel>
                    <textarea
                      {...field}
                      id="form-listing-description"
                      rows={4}
                      placeholder="Tell people about the place..."
                      className="rounded-md border bg-background px-3 py-2 text-sm"
                    />
                    {fieldState.invalid && (
                      <FieldError errors={[fieldState.error]} />
                    )}
                  </Field>
                )}
              />

              <Controller
                name="price"
                control={form.control}
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="form-listing-price">Price / month</FieldLabel>
                    <Input
                      {...field}
                      id="form-listing-price"
                      aria-invalid={fieldState.invalid}
                      type="number"
                      placeholder="1200"
                    />
                    {fieldState.invalid && (
                      <FieldError errors={[fieldState.error]} />
                    )}
                  </Field>
                )}
              />

              <Controller
                name="location"
                control={form.control}
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="form-listing-location">Location</FieldLabel>
                    <Input
                      {...field}
                      id="form-listing-location"
                      aria-invalid={fieldState.invalid}
                      placeholder="Berkeley, CA"
                    />
                    {fieldState.invalid && (
                      <FieldError errors={[fieldState.error]} />
                    )}
                  </Field>
                )}
              />

              <Controller
                name="room_type"
                control={form.control}
                render={({ field }) => (
                  <Field>
                    <FieldLabel htmlFor="form-listing-roomtype">
                      Room type (optional)
                    </FieldLabel>
                    <Input
                      {...field}
                      id="form-listing-roomtype"
                      placeholder="studio, 1br, shared..."
                    />
                  </Field>
                )}
              />

              <Controller
                name="sqft"
                control={form.control}
                render={({ field }) => (
                  <Field>
                    <FieldLabel htmlFor="form-listing-sqft">
                      Sqft (optional)
                    </FieldLabel>
                    <Input
                      {...field}
                      id="form-listing-sqft"
                      type="number"
                    />
                  </Field>
                )}
              />

              <Controller
                name="start_date"
                control={form.control}
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="form-listing-start">Start date</FieldLabel>
                    <Input
                      {...field}
                      id="form-listing-start"
                      aria-invalid={fieldState.invalid}
                      type="date"
                    />
                    {fieldState.invalid && (
                      <FieldError errors={[fieldState.error]} />
                    )}
                  </Field>
                )}
              />

              <Controller
                name="end_date"
                control={form.control}
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="form-listing-end">End date</FieldLabel>
                    <Input
                      {...field}
                      id="form-listing-end"
                      type="date"
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
          <Field orientation="horizontal">
            <Button
              type="button"
              variant="outline"
              onClick={() => form.reset()}
            >
              Reset
            </Button>
            <Button type="submit" form="form-listing">
              Post listing
            </Button>
          </Field>
        </CardFooter>
      </Card>
    </div>
  );
}
