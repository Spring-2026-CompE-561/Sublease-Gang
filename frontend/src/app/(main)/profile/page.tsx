"use client";

import { useEffect, useState } from "react";
import {
  User, Mail, Phone, Pencil,
  X, Check, Loader2, AtSign, FileText
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { clearTokens, getAccessToken } from "@/lib/auth";
import { ApiUnauthorizedError } from "@/lib/api";
import { profileService } from "@/lib/profileService";
import type { UserResponse, ProfileResponse } from "@/lib/profile";

export default function Profile() {
  const router = useRouter();
  const token = getAccessToken();

  const [user, setUser] = useState<UserResponse | null>(null);
  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  // Separate form state for user vs profile fields
  const [userForm, setUserForm] = useState({ email: "", username: "" });
  const [profileForm, setProfileForm] = useState({
    firstname: "",
    lastname: "",
    contact_email: "",
    contact_phone: "",
    description: "",
  });

  useEffect(() => {
    if (!token) {
      router.push("/signin");
      return;
    }

    const load = async () => {
      try {
        const [userData, profileData] = await Promise.all([
          profileService.getMe(token),
          profileService.getMyProfile(token),
        ]);
        setUser(userData);
        setProfile(profileData);
        setUserForm({ email: userData.email, username: userData.username });
        setProfileForm({
          firstname: profileData.firstname,
          lastname: profileData.lastname,
          contact_email: profileData.contact_email ?? "",
          contact_phone: profileData.contact_phone ?? "",
          description: profileData.description ?? "",
        });
      } catch (err) {
        if (err instanceof ApiUnauthorizedError) {
          return;
        }
        toast.error("Failed to load profile");
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, [token, router]);

  const handleSave = async () => {
    if (!token) return;
    setIsSaving(true);
    try {
      // Only send fields that actually changed
      const userPayload: Record<string, string> = {};
      if (userForm.email !== user?.email) userPayload.email = userForm.email;
      if (userForm.username !== user?.username) userPayload.username = userForm.username;

      const profilePayload: Record<string, string> = {};
      if (userForm.username !== user?.username) {
        profilePayload.username = userForm.username;
      }
      if (profileForm.firstname !== profile?.firstname) profilePayload.firstname = profileForm.firstname;
      if (profileForm.lastname !== profile?.lastname) profilePayload.lastname = profileForm.lastname;
      if (profileForm.contact_email !== (profile?.contact_email ?? "")) profilePayload.contact_email = profileForm.contact_email;
      if (profileForm.contact_phone !== (profile?.contact_phone ?? "")) profilePayload.contact_phone = profileForm.contact_phone;
      if (profileForm.description !== (profile?.description ?? "")) profilePayload.description = profileForm.description;

      // Fire both updates in parallel if needed
      const updates: Promise<unknown>[] = [];
      if (Object.keys(userPayload).length > 0)
        updates.push(profileService.updateMe(token, userPayload).then(setUser));
      if (Object.keys(profilePayload).length > 0)
        updates.push(profileService.updateMyProfile(token, profilePayload).then(setProfile));

      if (updates.length === 0) {
        setIsSaving(false);
        toast("No changes to save");
        setIsEditing(false);
        return;
      }

      await Promise.all(updates);
      setIsEditing(false);
      toast.success("Profile updated successfully");
    } catch (err) {
      if (err instanceof ApiUnauthorizedError) {
        return;
      }
      const message = err instanceof Error ? err.message : "Failed to update profile";
      toast.error(message);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setUserForm({ email: user?.email ?? "", username: user?.username ?? "" });
    setProfileForm({
      firstname: profile?.firstname ?? "",
      lastname: profile?.lastname ?? "",
      contact_email: profile?.contact_email ?? "",
      contact_phone: profile?.contact_phone ?? "",
      description: profile?.description ?? "",
    });
    setIsEditing(false);
  };

  const handleSignOut = () => { clearTokens(); router.push("/"); };

  const handleDeleteAccount = async () => {
    if (!token) return;
    const confirmed = window.confirm(
      "Delete your account? This cannot be undone."
    );
    if (!confirmed) return;

    setIsSaving(true);
    try {
      await profileService.deleteMe(token);
      clearTokens();
      toast.success("Your account has been deleted.");
      router.push("/");
    } catch (err) {
      if (err instanceof ApiUnauthorizedError) {
        return;
      }
      const message = err instanceof Error ? err.message : "Failed to delete account";
      toast.error(message);
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-24">
        <Loader2 className="size-8 animate-spin text-gray-400" />
      </div>
    );
  }

  const displayName = profile
    ? `${profile.firstname} ${profile.lastname}`
    : user?.username ?? "Student Profile";

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-3xl mx-auto space-y-6">

        {/* Profile Header */}
        <Card className="p-6">
          <div className="flex flex-col sm:flex-row items-center gap-6">
            <Avatar className="size-24">
              <AvatarFallback className="bg-gray-200">
                <User className="size-12 text-gray-500" />
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 text-center sm:text-left">
              {isEditing ? (
                <div className="flex gap-2 mb-3">
                  <div className="space-y-1 flex-1">
                    <Label className="text-xs text-gray-500">First Name</Label>
                    <Input
                      value={profileForm.firstname}
                      onChange={e => setProfileForm(f => ({ ...f, firstname: e.target.value }))}
                      className="h-9 text-sm"
                    />
                  </div>
                  <div className="space-y-1 flex-1">
                    <Label className="text-xs text-gray-500">Last Name</Label>
                    <Input
                      value={profileForm.lastname}
                      onChange={e => setProfileForm(f => ({ ...f, lastname: e.target.value }))}
                      className="h-9 text-sm"
                    />
                  </div>
                </div>
              ) : (
                <h1 className="text-2xl font-semibold mb-1">{displayName}</h1>
              )}
              <div className="flex items-center justify-center sm:justify-start gap-2 text-gray-600 mb-4">
                <span className="size-2 rounded-full bg-green-500 inline-block" />
                <span className="text-sm">University Verified</span>
              </div>
              {!isEditing ? (
                <Button variant="outline" className="min-h-[44px] text-sm gap-2" onClick={() => setIsEditing(true)}>
                  <Pencil className="size-4" /> Edit Profile
                </Button>
              ) : (
                <div className="flex gap-2">
                  <Button className="min-h-[44px] text-sm gap-2 bg-red-600 hover:bg-red-700" onClick={handleSave} disabled={isSaving}>
                    {isSaving ? <Loader2 className="size-4 animate-spin" /> : <Check className="size-4" />}
                    Save
                  </Button>
                  <Button variant="outline" className="min-h-[44px] text-sm gap-2" onClick={handleCancel} disabled={isSaving}>
                    <X className="size-4" /> Cancel
                  </Button>
                </div>
              )}
            </div>
          </div>
        </Card>

        {/* Contact Information */}
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Contact Information</h2>
          <div className="space-y-5">

            {/* Email (account) — read-only, from UserResponse */}
            <div className="flex items-start gap-3">
              <Mail className="size-5 text-gray-400 mt-0.5" />
              <div className="flex-1">
                <p className="text-xs text-gray-500">Account Email</p>
                <p className="text-sm">{user?.email}</p>
              </div>
            </div>

            <Separator />

            {/* Username */}
            <div className="flex items-start gap-3">
              <AtSign className="size-5 text-gray-400 mt-2" />
              <div className="flex-1">
                {isEditing ? (
                  <div className="space-y-1">
                    <Label className="text-xs text-gray-500">Username</Label>
                    <Input
                      value={userForm.username}
                      onChange={e => setUserForm(f => ({ ...f, username: e.target.value }))}
                      className="h-9 text-sm"
                      placeholder="username"
                    />
                  </div>
                ) : (
                  <>
                    <p className="text-xs text-gray-500">Username</p>
                    <p className="text-sm">{user?.username}</p>
                  </>
                )}
              </div>
            </div>

            <Separator />

            {/* Contact Phone — from ProfileResponse */}
            <div className="flex items-start gap-3">
              <Phone className="size-5 text-gray-400 mt-2" />
              <div className="flex-1">
                {isEditing ? (
                  <div className="space-y-1">
                    <Label className="text-xs text-gray-500">Phone</Label>
                    <Input
                      value={profileForm.contact_phone}
                      onChange={e => setProfileForm(f => ({ ...f, contact_phone: e.target.value }))}
                      className="h-9 text-sm"
                      placeholder="+1 (555) 000-0000"
                    />
                  </div>
                ) : (
                  <>
                    <p className="text-xs text-gray-500">Phone</p>
                    <p className="text-sm">{profile?.contact_phone || "—"}</p>
                  </>
                )}
              </div>
            </div>

            <Separator />

            {/* Contact Email — from ProfileResponse (can differ from account email) */}
            <div className="flex items-start gap-3">
              <Mail className="size-5 text-gray-400 mt-2" />
              <div className="flex-1">
                {isEditing ? (
                  <div className="space-y-1">
                    <Label className="text-xs text-gray-500">Contact Email</Label>
                    <Input
                      value={profileForm.contact_email}
                      onChange={e => setProfileForm(f => ({ ...f, contact_email: e.target.value }))}
                      className="h-9 text-sm"
                      placeholder="contact@example.com"
                    />
                  </div>
                ) : (
                  <>
                    <p className="text-xs text-gray-500">Contact Email</p>
                    <p className="text-sm">{profile?.contact_email || "—"}</p>
                  </>
                )}
              </div>
            </div>

            <Separator />

            {/* Description */}
            <div className="flex items-start gap-3">
              <FileText className="size-5 text-gray-400 mt-2" />
              <div className="flex-1">
                {isEditing ? (
                  <div className="space-y-1">
                    <Label className="text-xs text-gray-500">
                      Bio <span className="text-gray-400">({profileForm.description.length}/500)</span>
                    </Label>
                    <Textarea
                      value={profileForm.description}
                      onChange={e => setProfileForm(f => ({ ...f, description: e.target.value }))}
                      className="text-sm resize-none"
                      rows={3}
                      maxLength={500}
                      placeholder="Tell others about yourself..."
                    />
                  </div>
                ) : (
                  <>
                    <p className="text-xs text-gray-500">Bio</p>
                    <p className="text-sm">{profile?.description || "—"}</p>
                  </>
                )}
              </div>
            </div>

          </div>
        </Card>

        {/* Settings */}
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Settings</h2>
          <div className="flex flex-col">
            <Button variant="ghost" className="w-full justify-start min-h-[44px] text-sm font-normal">
              Notification Preferences
            </Button>
            <Separator />
            <Button variant="ghost" className="w-full justify-start min-h-[44px] text-sm font-normal">
              Privacy Settings
            </Button>
            <Separator />
            <Button variant="ghost" className="w-full justify-start min-h-[44px] text-sm font-normal">
              Payment Methods
            </Button>
            <Separator />
            <Button
              variant="ghost"
              onClick={handleSignOut}
              className="w-full justify-start min-h-[44px] text-sm font-normal text-red-600 hover:text-red-600 hover:bg-red-50"
            >
              Sign Out
            </Button>
            <Separator />
            <Button
              variant="ghost"
              onClick={handleDeleteAccount}
              disabled={isSaving}
              className="w-full justify-start min-h-[44px] text-sm font-normal text-red-600 hover:text-red-600 hover:bg-red-50"
            >
              Delete account
            </Button>
          </div>
        </Card>

      </div>
    </div>
  );
}
