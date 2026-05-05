"use client";

import { useCallback, useEffect, useState } from "react";
import { User, Mail, Phone, Loader2 } from "lucide-react";
import { useParams, useRouter } from "next/navigation";
import { Card } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";
import { ApiUnauthorizedError } from "@/lib/api";
import {
  AUTH_CHANGED_EVENT,
  clearTokens,
  getAccessToken,
} from "@/lib/auth";
import { profileService, type ListingsResponse } from "@/lib/profileService";
import type { ProfileResponse } from "@/lib/profile";
import { Listing } from "@/types/listing";
import { ListingCard } from "@/components/ListingCard";

export default function PublicUserProfile() {
  const params = useParams();
  const router = useRouter();
  const username = params.username as string;

  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [listings, setListings] = useState<ListingsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const load = useCallback(async () => {
    const token = getAccessToken();
    if (!token) {
      setIsLoading(false);
      router.replace("/signin");
      return;
    }

    setIsLoading(true);
    try {
      const profileData = await profileService.getPublicProfile(token, username);
      setProfile(profileData);

      const listingsData = await profileService.getUserListings(
        token,
        profileData.user_id,
      );
      setListings(listingsData);
    } catch (e) {
      if (e instanceof ApiUnauthorizedError) {
        clearTokens();
        toast.error(e.message);
        router.replace("/signin");
        return;
      }
      toast.error("Failed to load user profile");
      setProfile(null);
      setListings(null);
    } finally {
      setIsLoading(false);
    }
  }, [router, username]);

  useEffect(() => {
    void load();
  }, [load]);

  // Sign-out only clears localStorage; this page would keep showing cached data
  // until the user navigates. Re-check when auth state changes (same tab).
  useEffect(() => {
    const onAuthChanged = () => {
      if (!getAccessToken()) {
        setProfile(null);
        setListings(null);
        setIsLoading(false);
        router.replace("/signin");
      }
    };
    window.addEventListener(AUTH_CHANGED_EVENT, onAuthChanged);
    return () => window.removeEventListener(AUTH_CHANGED_EVENT, onAuthChanged);
  }, [router]);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-24">
        <Loader2 className="size-8 animate-spin text-gray-400" />
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <p className="text-gray-500">User profile not found</p>
        </div>
      </div>
    );
  }

  const displayName = `${profile.firstname} ${profile.lastname}`;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto space-y-8">

        {/* Profile Header */}
        <Card className="p-6">
          <div className="flex flex-col sm:flex-row items-start gap-6">
            <Avatar className="size-24">
              <AvatarFallback className="bg-gray-200">
                <User className="size-12 text-gray-500" />
              </AvatarFallback>
            </Avatar>
            <div className="flex-1">
              <h1 className="text-3xl font-bold mb-2">{displayName}</h1>
              <div className="flex items-center gap-2 text-gray-600 mb-4">
                <span className="size-2 rounded-full bg-green-500 inline-block" />
                <span className="text-sm">University Verified</span>
              </div>
              {profile.description && (
                <div className="mb-4">
                  <p className="text-gray-700">{profile.description}</p>
                </div>
              )}
            </div>
          </div>
        </Card>

        {/* Contact Information */}
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Contact Information</h2>
          <div className="space-y-5">
            {profile.contact_email && (
              <>
                <div className="flex items-start gap-3">
                  <Mail className="size-5 text-gray-400 mt-0.5" />
                  <div>
                    <p className="text-xs text-gray-500">Email</p>
                    <p className="text-sm">{profile.contact_email}</p>
                  </div>
                </div>
                <Separator />
              </>
            )}

            {profile.contact_phone && (
              <>
                <div className="flex items-start gap-3">
                  <Phone className="size-5 text-gray-400 mt-0.5" />
                  <div>
                    <p className="text-xs text-gray-500">Phone</p>
                    <p className="text-sm">{profile.contact_phone}</p>
                  </div>
                </div>
                <Separator />
              </>
            )}

            <div className="flex items-start gap-3">
              <User className="size-5 text-gray-400 mt-0.5" />
              <div>
                <p className="text-xs text-gray-500">Username</p>
                <p className="text-sm">{profile.username}</p>
              </div>
            </div>
          </div>
        </Card>

        {/* Listings */}
        <div>
          <h2 className="text-lg font-semibold mb-6">
            Listings ({listings?.count ?? 0})
          </h2>
          {listings && listings.results.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {listings.results.map((item) => {
                const listing: Listing = {
                  id: item.id,
                  host_id: profile.user_id,
                  title: item.title,
                  description: item.description,
                  price: item.price,
                  location: item.location_text,
                  room_type: item.room_type,
                  sqft: item.sqft,
                  start_date: item.start_date || new Date().toISOString(),
                  end_date: item.end_date || new Date().toISOString(),
                  thumbnail_url: item.thumbnail_url || undefined,
                  image_urls: item.image_urls,
                  latitude: item.latitude || 0,
                  longitude: item.longitude || 0,
                  created_at: item.created_at || new Date().toISOString(),
                  updated_at: item.created_at || new Date().toISOString(),
                };
                return <ListingCard key={listing.id} listing={listing} />;
              })}
            </div>
          ) : (
            <Card className="p-12 text-center">
              <p className="text-gray-500">No listings available</p>
            </Card>
          )}
        </div>

      </div>
    </div>
  );
}
