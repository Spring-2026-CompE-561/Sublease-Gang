"use client";

import { useCallback, useEffect, useRef, useState } from "react";
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
import { useForm, Controller, useFieldArray } from "react-hook-form";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { Upload, X } from "lucide-react";
import { API_BASE_URL, ACCESS_TOKEN_KEY, readApiErrorMessage, postApiJson, ApiUnauthorizedError } from "@/lib/api";
import type { Listing } from "@/types/listing";

const MAX_PHOTOS = 12;
const MAX_IMAGE_BYTES = 1_500_000;

const NOMINATIM_URL = "https://nominatim.openstreetmap.org/search";

async function geocodeAddress(query: string): Promise<{ lat: number; lng: number } | null> {
	const url = `${NOMINATIM_URL}?format=jsonv2&limit=1&q=${encodeURIComponent(query)}`;
	const res = await fetch(url, { headers: { Accept: "application/json" } });
	if (!res.ok) return null;
	const data = (await res.json()) as Array<{ lat?: string; lon?: string }>;
	const hit = data[0];
	if (!hit?.lat || !hit?.lon) return null;
	const lat = Number(hit.lat);
	const lng = Number(hit.lon);
	if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null;
	return { lat, lng };
}

const photoRowSchema = z.object({
	id: z.string(),
	url: z.string().min(1),
});

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
	photos: z
		.array(photoRowSchema)
		.min(1, "Add at least one photo")
		.max(MAX_PHOTOS, `You can add up to ${MAX_PHOTOS} photos`),
});

type FormValues = z.infer<typeof formSchema>;

function splitStoredLocation(stored: string): { address: string; city: string } {
	const idx = stored.lastIndexOf(", ");
	if (idx === -1) return { address: "", city: stored };
	return { address: stored.slice(0, idx), city: stored.slice(idx + 2) };
}

function isoToDateInput(iso: string | null | undefined): string {
	if (!iso) return "";
	return iso.slice(0, 10);
}

function defaultsFromListing(listing: Listing): FormValues {
	const { address, city } = splitStoredLocation(listing.location);
	return {
		title: listing.title ?? "",
		description: listing.description ?? "",
		price: listing.price != null ? String(listing.price) : "",
		address,
		location: city,
		room_type: listing.room_type ?? "",
		sqft: listing.sqft != null ? String(listing.sqft) : "",
		start_date: isoToDateInput(listing.start_date),
		end_date: isoToDateInput(listing.end_date),
		photos: (listing.image_urls ?? []).map((url) => ({
			id: crypto.randomUUID(),
			url,
		})),
	};
}

function readFileAsDataUrl(file: File): Promise<string> {
	return new Promise((resolve, reject) => {
		const reader = new FileReader();
		reader.onload = () => {
			if (typeof reader.result === "string") resolve(reader.result);
			else reject(new Error("Invalid read result"));
		};
		reader.onerror = () => reject(reader.error ?? new Error("read failed"));
		reader.readAsDataURL(file);
	});
}

type ListingFormProps = React.ComponentProps<"div"> & {
	mode?: "create" | "edit";
	listing?: Listing;
	listingId?: number;
};

export function ListingForm({
	className,
	mode = "create",
	listing,
	listingId,
	...props
}: ListingFormProps) {
	const router = useRouter();
	const fileInputRef = useRef<HTMLInputElement>(null);
	const dragPhotoFrom = useRef<number | null>(null);
	const [dropZoneActive, setDropZoneActive] = useState(false);
	const [isAuthChecked] = useState(() =>
		typeof window !== "undefined" && !!localStorage.getItem(ACCESS_TOKEN_KEY)
	);

	const isEdit = mode === "edit" && listing !== undefined && listingId !== undefined;

	// Check authentication before showing form
	useEffect(() => {
		if (!isAuthChecked) {
			toast.error("You need to sign in first");
			router.push("/signin");
		}
	}, [isAuthChecked, router]);

	const form = useForm<FormValues>({
		resolver: zodResolver(formSchema),
		defaultValues:
			isEdit && listing
				? defaultsFromListing(listing)
				: {
						title: "",
						description: "",
						price: "",
						address: "",
						location: "",
						room_type: "",
						sqft: "",
						start_date: "",
						end_date: "",
						photos: [],
					},
	});

	const { fields, append, remove, move } = useFieldArray({
		control: form.control,
		name: "photos",
	});

	const addImageFiles = useCallback(
		async (files: FileList | File[]) => {
			const list = Array.from(files).filter((f) => f.type.startsWith("image/"));
			if (list.length === 0) {
				toast.error("Please choose image files");
				return;
			}
			const current = form.getValues("photos").length;
			let added = 0;
			for (const file of list) {
				if (current + added >= MAX_PHOTOS) {
					toast.info(`Maximum ${MAX_PHOTOS} photos`);
					break;
				}
				if (file.size > MAX_IMAGE_BYTES) {
					toast.error(`${file.name} is over 1.5 MB — skip or compress it`);
					continue;
				}
				try {
					const url = await readFileAsDataUrl(file);
					append({ id: crypto.randomUUID(), url });
					added += 1;
				} catch {
					toast.error(`Could not read ${file.name}`);
				}
			}
			if (added > 0) {
				void form.trigger("photos");
			}
		},
		[append, form],
	);

	function onFileInputChange(e: React.ChangeEvent<HTMLInputElement>) {
		const files = e.target.files;
		if (files?.length) void addImageFiles(files);
		e.target.value = "";
	}

	function onDropZoneDragOver(e: React.DragEvent) {
		e.preventDefault();
		e.stopPropagation();
		setDropZoneActive(true);
	}

	function onDropZoneDragLeave(e: React.DragEvent) {
		e.preventDefault();
		e.stopPropagation();
		if (e.currentTarget === e.target) setDropZoneActive(false);
	}

	function onDropZoneDrop(e: React.DragEvent) {
		e.preventDefault();
		e.stopPropagation();
		setDropZoneActive(false);
		const dt = e.dataTransfer.files;
		if (dt?.length) void addImageFiles(dt);
	}

	function onThumbDragStart(index: number) {
		dragPhotoFrom.current = index;
	}

	function onThumbDragOver(e: React.DragEvent) {
		e.preventDefault();
	}

	function onThumbDrop(toIndex: number) {
		const from = dragPhotoFrom.current;
		dragPhotoFrom.current = null;
		if (from == null || from === toIndex) return;
		move(from, toIndex);
	}

	function onThumbDragEnd() {
		dragPhotoFrom.current = null;
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
		const image_urls = data.photos.map((p) => p.url);

		const addressUnchanged =
			isEdit && listing ? combinedLocation === listing.location : false;

		let coords: { lat: number; lng: number } | null;
		if (addressUnchanged && listing) {
			coords = { lat: listing.latitude, lng: listing.longitude };
		} else {
			try {
				coords = await geocodeAddress(combinedLocation);
			} catch {
				toast.error(
					"Could not look up that address — check your connection and try again",
				);
				return;
			}
			if (!coords) {
				toast.error("Couldn't find that address. Double-check the street and city.");
				return;
			}
		}

		const payload = {
			title: data.title.trim(),
			description: data.description.trim(),
			price,
			location: combinedLocation,
			room_type: data.room_type.trim(),
			sqft: Number(data.sqft),
			start_date: new Date(data.start_date).toISOString(),
			end_date: new Date(data.end_date).toISOString(),
			image_urls,
			latitude: coords.lat,
			longitude: coords.lng,
		};

		try {
			if (isEdit && listingId !== undefined) {
				// Handle PUT request for edit - keep using fetch for now as we don't have putApiJson
				const res = await fetch(`${API_BASE_URL}/api/v1/listings/${listingId}`, {
					method: "PUT",
					headers: {
						"Content-Type": "application/json",
						Authorization: `Bearer ${token}`,
					},
					body: JSON.stringify(payload),
				});

				if (!res.ok) {
					const msg = (await readApiErrorMessage(res)) || res.statusText;
					toast.error(`Could not save changes: ${msg}`);
					return;
				}

				toast.success("Listing updated");
				router.push("/my-listings");
			} else {
				// Handle POST request for create - use postApiJson
				await postApiJson<Listing, typeof payload>("/api/v1/listings/", token, payload);
				toast.success("Listing posted");
				router.push("/");
			}
			router.refresh();
		} catch (e) {
			if (e instanceof ApiUnauthorizedError) {
				// SessionExpiredHandler will handle the redirect and toast
				return;
			}
			
			if (e instanceof Error) {
				const verb = isEdit ? "save changes" : "post listing";
				toast.error(`Could not ${verb}: ${e.message}`);
				console.log("listing submit failed", e);
			} else {
				toast.error("Something went wrong, try again");
				console.log("listing submit failed", e);
			}
		}
	}

	const photosError = form.formState.errors.photos;

	if (!isAuthChecked) {
		return null;
	}

	return (
		<div className={cn("flex flex-col gap-6", className)} {...props}>
			<Card>
				<CardHeader>
					<CardTitle>{isEdit ? "Edit listing" : "Post a sublease"}</CardTitle>
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

							<Field
								className="sm:col-span-2"
								data-invalid={Boolean(photosError)}
							>
								<FieldLabel htmlFor="form-listing-photos-trigger">Photos</FieldLabel>
								<p className="mb-3 text-sm text-muted-foreground" id="form-listing-photos-hint">
									Drag and drop images here or click to browse. First photo is the cover (up to{" "}
									{MAX_PHOTOS} images, 1.5 MB each).
								</p>

								<input
									ref={fileInputRef}
									id="form-listing-photos-input"
									type="file"
									accept="image/*"
									multiple
									className="sr-only"
									tabIndex={-1}
									aria-hidden
									onChange={onFileInputChange}
								/>

								<button
									id="form-listing-photos-trigger"
									type="button"
									onClick={() => fileInputRef.current?.click()}
									aria-describedby="form-listing-photos-hint"
									onDragOver={onDropZoneDragOver}
									onDragLeave={onDropZoneDragLeave}
									onDrop={onDropZoneDrop}
									className={cn(
										"flex w-full min-h-[140px] cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed px-4 py-8 text-center transition-colors",
										dropZoneActive
											? "border-primary bg-primary/5"
											: "border-muted-foreground/25 bg-muted/30 hover:border-muted-foreground/40 hover:bg-muted/50",
									)}
								>
									<Upload className="size-8 text-muted-foreground" aria-hidden />
									<span className="text-sm font-medium text-foreground">
										Drop images here or click to select
									</span>
									<span className="text-xs text-muted-foreground">
										{fields.length} / {MAX_PHOTOS} added
									</span>
								</button>

								{fields.length > 0 ? (
									<ul
										className="mt-4 grid w-full grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5"
										aria-label="Photo previews"
									>
										{fields.map((field, index) => (
											<li
												key={field.id}
												draggable
												onDragStart={() => onThumbDragStart(index)}
												onDragOver={onThumbDragOver}
												onDrop={() => onThumbDrop(index)}
												onDragEnd={onThumbDragEnd}
												className="group relative aspect-square overflow-hidden rounded-lg border bg-muted ring-offset-background focus-within:ring-2 focus-within:ring-ring"
											>
												{/* eslint-disable-next-line @next/next/no-img-element */}
												<img
													src={field.url}
													alt=""
													className="size-full object-cover"
												/>
												{index === 0 ? (
													<span className="absolute left-1.5 top-1.5 rounded bg-background/90 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-foreground shadow-sm">
														Cover
													</span>
												) : (
													<Button
														type="button"
														variant="secondary"
														size="sm"
														className="absolute left-1.5 top-1.5 h-7 px-2 text-[10px] font-medium opacity-0 transition-opacity group-hover:opacity-100 group-focus-within:opacity-100"
														onClick={() => move(index, 0)}
													>
														Make cover
													</Button>
												)}
												<Button
													type="button"
													size="icon"
													variant="destructive"
													className="absolute right-1 top-1 size-8 rounded-full opacity-0 shadow-md transition-opacity group-hover:opacity-100 group-focus-within:opacity-100"
													aria-label={`Remove photo ${index + 1}`}
													onClick={() => remove(index)}
												>
													<X className="size-4" />
												</Button>
												<span className="pointer-events-none absolute bottom-1 left-1 rounded bg-black/55 px-1.5 py-0.5 text-[10px] text-white">
													Drag to reorder
												</span>
											</li>
										))}
									</ul>
								) : null}

								{photosError?.message ? (
									<FieldError errors={[{ message: photosError.message }]} />
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
						</FieldGroup>
					</form>
				</CardContent>
				<CardFooter>
					<Field orientation="horizontal">
						{isEdit ? (
							<Button
								type="button"
								variant="outline"
								onClick={() => router.push("/my-listings")}
							>
								Cancel
							</Button>
						) : (
							<Button type="button" variant="outline" onClick={() => form.reset()}>
								Reset
							</Button>
						)}
						<Button type="submit" form="form-listing">
							{isEdit ? "Save changes" : "Post listing"}
						</Button>
					</Field>
				</CardFooter>
			</Card>
		</div>
	);
}
