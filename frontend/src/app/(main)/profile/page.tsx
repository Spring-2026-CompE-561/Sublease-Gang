import { User, Mail, Phone, MapPin } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";

export default function Profile() {
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
                </div>
            </Card>

            </div>
        </div>
    )
}