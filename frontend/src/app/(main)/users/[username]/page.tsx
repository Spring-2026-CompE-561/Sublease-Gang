"use client";

import { useEffect, useState } from "react";
import { User, Mail, Phone, Loader2 } from "lucide-react";
import { useParams } from "next/navigation";
import { Card } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";
import { profileService, type ListingsResponse } from "@/lib/profileService";
import type { UserResponse, ProfileResponse } from "@/lib/profile";
import { ListingCard } from "@/components/ListingCard";

export default function PublicUserProfile() {
  const params = useParams();
  const username = params.username as string;

  const [user, setUser] = useState<UserResponse | null>(null);
  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [listings, setListings] = useState<ListingsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const profileData = await profileService.getPublicProfile(username);
        setProfile(profileData);

        const userData = await profileService.getPublicUser(profileData.user_id);
        setUser(userData);

        const listingsData = await profileService.getUserListings(profileData.user_id);
        setListings(listingsData);
      } catch {
        toast.error("Failed to load user profile");
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, [username]);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-24">
        <Loader2 className="size-8 animate-spin text-gray-400" />
      </div>
    );
  }

  if (!profile || !user) {
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
                const listing = {
                  ...item,
                  location: item.location_text,
                  host_id: 0,
                  description: "",
                  latitude: 0,
                  longitude: 0,
                  created_at: item.created_at || new Date().toISOString(),
                  updated_at: new Date().toISOString(),
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
