"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { z } from "zod";
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Field,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { getAccessToken } from "@/lib/auth";

const formSchema = z.object({
  reason: z.enum(
    ["Listing is fake", "Inappropriate content", "Scam or fraud", "Duplicate listing", "Other"],
    { message: "Please select a reason." }
  ),
  details: z
    .string()
    .max(500, "Details must be 500 characters or less.")
    .optional()
    .or(z.literal("")),
});

type ReportListingValues = z.infer<typeof formSchema>;

interface ReportListingDialogProps {
  listingId: string;
}

export function ReportListingDialog({ listingId: _listingId }: ReportListingDialogProps) {
  const router = useRouter();
  const [open, setOpen] = useState(false);

  const form = useForm<ReportListingValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      reason: undefined,
      details: "",
    },
  });

  function handleOpenClick() {
    const token = getAccessToken();
    if (!token) {
      router.push("/signin");
      return;
    }
    setOpen(true);
  }

  function onSubmit(_data: ReportListingValues) {
    // TODO: Wire up to /api/v1/listings/{listingId}/report when backend exists
    // listingId should be sent with the report data above
    // TODO: Update toast message once API endpoint is ready
    toast.success("Thanks for your feedback.");
    setOpen(false);
    form.reset();
  }

  return (
    <>
      <Button
        variant="outline"
        onClick={handleOpenClick}
        className="mt-3 w-full justify-center rounded-xl"
      >
        Report listing
      </Button>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Report this listing</DialogTitle>
            <DialogDescription>
              Help us keep SubLease safe by reporting inappropriate or suspicious listings.
            </DialogDescription>
          </DialogHeader>

          <form id="form-report-listing" onSubmit={form.handleSubmit(onSubmit)}>
            <FieldGroup>
              <Controller
                name="reason"
                control={form.control}
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel>Reason</FieldLabel>
                    <Select value={field.value ?? ""} onValueChange={field.onChange}>
                      <SelectTrigger aria-invalid={fieldState.invalid}>
                        <SelectValue placeholder="Select a reason" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Listing is fake">Listing is fake</SelectItem>
                        <SelectItem value="Inappropriate content">Inappropriate content</SelectItem>
                        <SelectItem value="Scam or fraud">Scam or fraud</SelectItem>
                        <SelectItem value="Duplicate listing">Duplicate listing</SelectItem>
                        <SelectItem value="Other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                    {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
                  </Field>
                )}
              />
              <Controller
                name="details"
                control={form.control}
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor="form-report-details">
                      Details <span className="text-sm text-muted-foreground">(optional)</span>
                    </FieldLabel>
                    <Textarea
                      {...field}
                      id="form-report-details"
                      aria-invalid={fieldState.invalid}
                      placeholder="Please provide any additional details..."
                      maxLength={500}
                    />
                    <div className="mt-1 text-xs text-muted-foreground text-right">
                      {field.value?.length || 0}/500
                    </div>
                    {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
                  </Field>
                )}
              />
            </FieldGroup>
          </form>

          <div className="flex gap-2 justify-end">
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" form="form-report-listing">
              Submit report
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}