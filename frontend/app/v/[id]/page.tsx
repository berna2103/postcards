export const dynamic = 'force-dynamic';

import { supabase } from "@/lib/supabase";
import { redirect } from "next/navigation";
import Image from "next/image";
import { MapPin, Phone, Mail, Download, ArrowRight, Home } from "lucide-react";

export default async function TrackingPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  // Track the scan in Supabase
  await supabase.from("scans").insert({ prospect_id: parseInt(id) });

  const { data: prospect } = await supabase
    .from("prospects")
    .select("*")
    .eq("id", Number(id))
    .single();

  if (!prospect) {
    redirect(
      "https://www.realtyofamerica.com/real-estate-agents/Illinois/bernardo-jimenez",
    );
  }

  // Pre-population Helpers
  const encodedAddress = encodeURIComponent(prospect.address);
  const firstName = prospect.first_name;

  // --- Enticing Email Logic ---
  const emailSubject = encodeURIComponent(
    `Property Report Request: ${prospect.address}`,
  );
  const emailBody = encodeURIComponent(
    `Hi Bernardo,\n\nI just scanned your card for ${prospect.address}. I'd love to see the custom market report you prepared for me.\n\nBest,\n${firstName}`,
  );
  const mailtoUrl = `mailto:bernardo.jimenez@realtyofamerica.com?subject=${emailSubject}&body=${emailBody}`;

  // --- Enticing Text Message Logic ---
  const smsBody = encodeURIComponent(
    `Hi Bernardo, this is ${firstName}. I just scanned your card for ${prospect.address}. Can you send me my property report?`,
  );
  const smsUrl = `sms:7083140477&body=${smsBody}`;

  const cloudCmaUrl = `https://app.cloudcma.com/api_widget/aa79d94dc9b4bf80cd34ae3f7560d5c8/show?address=${encodedAddress}`;

  return (
    <main className="min-h-screen bg-[#F1F5F9] flex flex-col items-center justify-center p-4 antialiased selection:bg-blue-100">
      {/* Background Accent */}
      <div className="fixed top-0 left-0 w-full h-96 bg-slate-900 -z-10" />

      <div className="max-w-md w-full mt-8">
        <div className="bg-white rounded-[3.5rem] shadow-[0_40px_80px_-15px_rgba(0,0,0,0.2)] overflow-hidden border border-white">
          {/* Main Branding Section */}
          <div className="pt-12 px-10 text-center">
            <div className="relative h-20 w-full mb-8 px-4">
              <Image
                src="/roa-logo.png"
                alt="Realty of America"
                fill
                className="object-contain"
                priority
              />
            </div>

            {/* Profile Section */}
            <div className="relative inline-block group">
              <div className="relative h-36 w-36 rounded-[3rem] rotate-3 group-hover:rotate-0 transition-transform duration-700 bg-slate-100 overflow-hidden mx-auto shadow-xl border-[8px] border-white">
                <Image
                  src="/headshot.png"
                  alt="Bernardo Jimenez"
                  fill
                  priority
                  sizes="144px"
                  className="object-cover"
                />
              </div>
              <div className="absolute -bottom-1 -right-1 bg-blue-600 text-white p-3 rounded-2xl shadow-2xl z-10 border-4 border-white">
                <Home size={20} />
              </div>
            </div>

            <h1 className="mt-8 text-3xl font-black text-slate-900 tracking-tight leading-none">
              Bernardo Jimenez
            </h1>
            <p className="text-blue-600 text-xs font-black uppercase tracking-[0.2em] mt-3">
              Licensed Real Estate Broker
            </p>
          </div>

          {/* Personalization & Actions */}
          <div className="p-10 pt-10">
            <div className="bg-blue-50/50 rounded-[2.5rem] p-8 mb-8 border border-blue-100/50">
              <h2 className="text-2xl font-black text-slate-900 italic">
                {prospect.language === "es" ? "Hola" : "Hi"}{" "}
                {prospect.first_name},
              </h2>
              <div className="flex items-start gap-3 mt-4 text-slate-600">
                <MapPin size={20} className="text-blue-600 shrink-0 mt-1" />
                <p className="text-base leading-snug font-medium">
                  I have your custom report for:
                  <br />
                  <span className="text-slate-900 font-black block mt-1 text-lg leading-tight uppercase tracking-tight">
                    {prospect.address}
                  </span>
                </p>
              </div>
            </div>

            <div className="space-y-4">
              {/* Pre-populated CloudCMA Button */}
              <a
                href={cloudCmaUrl}
                className="flex items-center justify-between w-full bg-slate-900 hover:bg-black text-white font-black py-6 px-10 rounded-2xl transition-all shadow-2xl group text-lg"
              >
                <span>GET HOME VALUE</span>
                <ArrowRight
                  size={24}
                  className="group-hover:translate-x-2 transition-transform"
                />
              </a>

              {/* Text Message Action */}
              <a
                href={smsUrl}
                className="flex items-center justify-center gap-3 w-full bg-blue-600 hover:bg-blue-700 text-white font-black py-5 px-8 rounded-2xl transition-all shadow-lg"
              >
                <Phone size={20} fill="currentColor" />
                <span>TEXT ME FOR THE REPORT</span>
              </a>

              <a
                href="/api/vcard"
                className="flex items-center justify-center gap-3 w-full bg-white border-2 border-slate-100 hover:border-blue-300 text-slate-800 font-bold py-5 px-8 rounded-2xl transition-all shadow-sm"
              >
                <Download size={20} />
                <span>SAVE CONTACT INFO</span>
              </a>
            </div>

            {/* Contact Grid */}
            <div className="grid grid-cols-2 gap-4 mt-12 pt-8 border-t border-slate-100">
              <a
                href="tel:7083140477"
                className="flex flex-col items-center gap-2 text-[11px] font-black uppercase tracking-widest text-slate-400 hover:text-blue-600 transition-all"
              >
                <Phone size={20} /> Call
              </a>
              <a
                href={mailtoUrl}
                className="flex flex-col items-center gap-2 text-[11px] font-black uppercase tracking-widest text-slate-400 hover:text-blue-600 transition-all"
              >
                <Mail size={20} /> Email
              </a>
            </div>
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-12 mb-12 flex flex-col items-center space-y-8 px-10 text-center">
          <div className="relative h-16 w-16 opacity-60">
            <Image
              src="/equal-housing.png"
              alt="Equal Housing Opportunity"
              fill
              className="object-contain"
            />
          </div>
          <div className="space-y-3">
            <p className="text-[12px] text-slate-500 font-black uppercase tracking-[0.3em]">
              Hablo Español • Chicago, IL
            </p>
            <p className="text-[10px] text-slate-400 leading-relaxed font-medium max-w-xs mx-auto">
              © 2026 Realty of America. Each office is independently owned and
              operated. Bernardo Jimenez is a licensed real estate broker in
              Illinois. License # 475.218221
            </p>
          </div>
        </footer>
      </div>
    </main>
  );
}