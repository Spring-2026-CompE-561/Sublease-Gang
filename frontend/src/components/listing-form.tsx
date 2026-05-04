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
import { Textarea } from "@/components/ui/textarea";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm, Controller, useWatch } from "react-hook-form";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { API_BASE_URL, ACCESS_TOKEN_KEY, readApiErrorMessage } from "@/lib/api";

const MAX_IMAGE_BYTES = 1_500_000;

// TODO: lat/lng should come from a map picker. hardcoded for now
const DEFAULT_LAT = 0;
const DEFAULT_LNG = 0;

const formSchema = z.object({
	title: z.string().min(3, "Title is too short"),
	description: z.string().min(10, "Need a longer description"),
	price: z.string().min(1, "Price is required"),
	address: z.string().min(3, "Street address is required"),
	location: z.string().min(2, "City or area is required"),
	room_type: z.string().min(1, "Room type is required"),
	sqft: z
		.string()
		.min(1, "Square footage is required")
		.refine((s) => {
			const n = Number(s);
			return !Number.isNaN(n) && n > 0;
		}, "Enter a valid square footage"),
	start_date: z.string().min(1, "Pick a start date"),
	end_date: z.string().min(1, "Pick an end date"),
	thumbnailDataUrl: z.string().min(1, "Add a cover photo"),
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
			address: "",
			location: "",
			room_type: "",
			sqft: "",
			start_date: "",
			end_date: "",
			thumbnailDataUrl: "",
		},
	});

	function onCoverFileChange(e: React.ChangeEvent<HTMLInputElement>) {
		const file = e.target.files?.[0];
		if (!file) return;
		if (!file.type.startsWith("image/")) {
			toast.error("Please choose an image file");
			return;
		}
		if (file.size > MAX_IMAGE_BYTES) {
			toast.error("Image must be under 1.5 MB");
			return;
		}
		const reader = new FileReader();
		reader.onload = () => {
			const url = reader.result;
			if (typeof url === "string") {
				form.setValue("thumbnailDataUrl", url, { shouldValidate: true });
			}
		};
		reader.readAsDataURL(file);
	}

	async function onSubmit(data: FormValues) {
		const price = Number(data.price);
		if (Number.isNaN(price) || price <= 0) {
			toast.error("Price must be a number greater than 0");
			return;
		}

		if (new Date(data.end_date) <= new Date(data.start_date)) {
			toast.error("End date must be after start date");
			return;
		}

		const token = localStorage.getItem(ACCESS_TOKEN_KEY);
		if (!token) {
			toast.error("You need to sign in first");
			router.push("/signin");
			return;
		}

		const combinedLocation = `${data.address.trim()}, ${data.location.trim()}`;

		const payload = {
			title: data.title.trim(),
			description: data.description.trim(),
			price,
			location: combinedLocation,
			room_type: data.room_type.trim(),
			sqft: Number(data.sqft),
			start_date: new Date(data.start_date).toISOString(),
			end_date: new Date(data.end_date).toISOString(),
			thumbnail_url: data.thumbnailDataUrl,
			latitude: DEFAULT_LAT,
			longitude: DEFAULT_LNG,
		};

		try {
			const res = await fetch(`${API_BASE_URL}/api/v1/listings/`, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
					Authorization: `Bearer ${token}`,
				},
				body: JSON.stringify(payload),
			});

			if (!res.ok) {
				const msg = (await readApiErrorMessage(res)) || res.statusText;
				toast.error("Could not post listing: " + msg);
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

	const thumb = useWatch({ control: form.control, name: "thumbnailDataUrl" });

	return (
		<div className={cn("flex flex-col gap-6", className)} {...props}>
			<Card>
				<CardHeader>
					<CardTitle>Post a sublease</CardTitle>
				</CardHeader>
				<CardContent>
					<form id="form-listing" onSubmit={form.handleSubmit(onSubmit)}>
						<FieldGroup className="grid gap-6 sm:grid-cols-2">
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
										{fieldState.invalid && <FieldError errors={[fieldState.error]} />}
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
											min={1}
											step={1}
											placeholder="1200"
										/>
										{fieldState.invalid && <FieldError errors={[fieldState.error]} />}
									</Field>
								)}
							/>

							<Controller
								name="address"
								control={form.control}
								render={({ field, fieldState }) => (
									<Field data-invalid={fieldState.invalid} className="sm:col-span-2">
										<FieldLabel htmlFor="form-listing-address">Street address</FieldLabel>
										<Input
											{...field}
											id="form-listing-address"
											aria-invalid={fieldState.invalid}
											placeholder="123 College Ave, Apt 4"
										/>
										{fieldState.invalid && <FieldError errors={[fieldState.error]} />}
									</Field>
								)}
							/>

							<Controller
								name="location"
								control={form.control}
								render={({ field, fieldState }) => (
									<Field data-invalid={fieldState.invalid} className="sm:col-span-2">
										<FieldLabel htmlFor="form-listing-location">City / neighborhood</FieldLabel>
										<Input
											{...field}
											id="form-listing-location"
											aria-invalid={fieldState.invalid}
											placeholder="Berkeley, CA"
										/>
										{fieldState.invalid && <FieldError errors={[fieldState.error]} />}
									</Field>
								)}
							/>

							<Controller
								name="description"
								control={form.control}
								render={({ field, fieldState }) => (
									<Field data-invalid={fieldState.invalid} className="sm:col-span-2">
										<FieldLabel htmlFor="form-listing-description">Description</FieldLabel>
										<Textarea
											{...field}
											id="form-listing-description"
											rows={4}
											placeholder="Tell people about the place..."
											aria-invalid={fieldState.invalid}
										/>
										{fieldState.invalid && <FieldError errors={[fieldState.error]} />}
									</Field>
								)}
							/>

							<Controller
								name="room_type"
								control={form.control}
								render={({ field, fieldState }) => (
									<Field data-invalid={fieldState.invalid}>
										<FieldLabel htmlFor="form-listing-roomtype">Room type</FieldLabel>
										<Input
											{...field}
											id="form-listing-roomtype"
											aria-invalid={fieldState.invalid}
											placeholder="Studio, 1BR, shared room…"
										/>
										{fieldState.invalid && <FieldError errors={[fieldState.error]} />}
									</Field>
								)}
							/>

							<Controller
								name="sqft"
								control={form.control}
								render={({ field, fieldState }) => (
									<Field data-invalid={fieldState.invalid}>
										<FieldLabel htmlFor="form-listing-sqft">Square feet</FieldLabel>
										<Input
											{...field}
											id="form-listing-sqft"
											aria-invalid={fieldState.invalid}
											type="number"
											min={1}
											step={1}
											placeholder="500"
										/>
										{fieldState.invalid && <FieldError errors={[fieldState.error]} />}
									</Field>
								)}
							/>

							<Field className="sm:col-span-2" data-invalid={Boolean(form.formState.errors.thumbnailDataUrl)}>
								<FieldLabel htmlFor="form-listing-cover">Cover photo</FieldLabel>
								<input
									id="form-listing-cover"
									type="file"
									accept="image/*"
									className="block w-full max-w-md text-sm file:mr-3 file:rounded-md file:border file:bg-muted file:px-3 file:py-1.5"
									onChange={onCoverFileChange}
								/>
								{thumb ? (
									<div className="relative mt-3 aspect-video w-full max-w-md overflow-hidden rounded-lg border bg-muted">
										{/* eslint-disable-next-line @next/next/no-img-element */}
										<img src={thumb} alt="Cover preview" className="size-full object-cover" />
									</div>
								) : null}
								{form.formState.errors.thumbnailDataUrl ? (
									<FieldError errors={[form.formState.errors.thumbnailDataUrl]} />
								) : null}
							</Field>

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
										{fieldState.invalid && <FieldError errors={[fieldState.error]} />}
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
											aria-invalid={fieldState.invalid}
											type="date"
										/>
										{fieldState.invalid && <FieldError errors={[fieldState.error]} />}
									</Field>
								)}
							/>

							<input type="hidden" {...form.register("thumbnailDataUrl")} />
						</FieldGroup>
					</form>
				</CardContent>
				<CardFooter>
					<Field orientation="horizontal">
						<Button type="button" variant="outline" onClick={() => form.reset()}>
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
