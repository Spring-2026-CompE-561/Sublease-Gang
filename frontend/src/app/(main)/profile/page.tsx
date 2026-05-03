"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { User, Mail, Phone, MapPin } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import {
    Dialog,
    DialogClose,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import { API_BASE_URL, readApiErrorMessage } from "@/lib/api";
import { clearTokens, getAccessToken } from "@/lib/auth";

export default function Profile() {
    const router = useRouter();
    const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);

    async function handleDeleteAccount() {
        const accessToken = getAccessToken();
        if (!accessToken) {
            toast.error("You must be signed in to delete your account.");
            router.push("/signin");
            return;
        }

        setIsDeleting(true);
        try {
            const response = await fetch(`${API_BASE_URL}/api/v1/users/me`, {
                method: "DELETE",
                headers: {
                    Authorization: `Bearer ${accessToken}`,
                },
            });

            if (!response.ok) {
                const apiErrorMessage = await readApiErrorMessage(response);
                toast.error(
                    `Failed to delete account: ${apiErrorMessage ?? response.statusText}`,
                );
                return;
            }

            clearTokens();
            setDeleteDialogOpen(false);
            toast.success("Your account has been deleted.");
            router.push("/");
        } catch (error) {
            const message = error instanceof Error ? error.message : String(error);
            toast.error(`Failed to delete account: ${message}`);
        } finally {
            // Always reset so a failed navigation or unexpected throw can't
            // leave the confirm button stuck on "Deleting...".
            setIsDeleting(false);
        }
    }

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
                    <h1 className="text-2xl font-semibold mb-2">Student Profile</h1>
                    {/* Green dot + "University Verified" to match screenshot */}
                    <div className="flex items-center justify-center sm:justify-start gap-2 text-gray-600 mb-4">
                    <span className="size-2 rounded-full bg-green-500 inline-block" />
                    <span className="text-sm">University Verified</span>
                    </div>
                    <Button variant="outline" className="min-h-[44px] text-sm">
                    Edit Profile
                    </Button>
                </div>
                </div>
            </Card>

            {/* Contact Information */}
            <Card className="p-6">
                <h2 className="text-lg font-semibold mb-4">Contact Information</h2>
                <div className="space-y-4">
                <div className="flex items-start gap-3">
                    <Mail className="size-5 text-gray-400 mt-0.5" />
                    <div>
                    <p className="text-xs text-gray-500">Email</p>
                    <p className="text-sm">student@university.edu</p>
                    </div>
                </div>
                <div className="flex items-start gap-3">
                    <Phone className="size-5 text-gray-400 mt-0.5" />
                    <div>
                    <p className="text-xs text-gray-500">Phone</p>
                    <p className="text-sm">+1 (123) 456-4321</p>
                    </div>
                </div>
                <div className="flex items-start gap-3">
                    <MapPin className="size-5 text-gray-400 mt-0.5" />
                    <div>
                    <p className="text-xs text-gray-500">University</p>
                    <p className="text-sm">Your University</p>
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
                    className="w-full justify-start min-h-[44px] text-sm font-normal text-red-600 hover:text-red-600 hover:bg-red-50"
                >
                    Sign Out
                </Button>
                <Separator />
                <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
                    <DialogTrigger
                        render={
                            <Button
                                variant="ghost"
                                className="w-full justify-start min-h-[44px] text-sm font-normal text-red-600 hover:text-red-600 hover:bg-red-50"
                            />
                        }
                    >
                        Delete Account
                    </DialogTrigger>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle>Delete account?</DialogTitle>
                            <DialogDescription>
                                This will permanently delete your account, listings, and messages. This action cannot be undone.
                            </DialogDescription>
                        </DialogHeader>
                        <DialogFooter>
                            <DialogClose
                                render={
                                    <Button
                                        variant="outline"
                                        className="min-h-[44px] text-sm"
                                        disabled={isDeleting}
                                    >
                                        Cancel
                                    </Button>
                                }
                            />
                            <Button
                                variant="ghost"
                                className="min-h-[44px] text-sm font-medium text-red-600 hover:text-red-600 hover:bg-red-50"
                                onClick={handleDeleteAccount}
                                disabled={isDeleting}
                            >
                                {isDeleting ? "Deleting..." : "Delete Account"}
                            </Button>
                        </DialogFooter>
                    </DialogContent>
                </Dialog>
                </div>
            </Card>

            </div>
        </div>
    )
}
