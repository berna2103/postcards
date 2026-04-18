import { NextResponse } from 'next/server';

export async function GET() {
  const vcard = `BEGIN:VCARD
VERSION:3.0
N:Jimenez;Bernardo;;;
FN:Bernardo Jimenez
ORG:Realty of America
TITLE:Licensed Real Estate Broker
TEL;TYPE=CELL:7083140477
EMAIL:bernardo.jimenez@realtyofamerica.com
URL:https://barcias.com
ADR;TYPE=WORK:;;Berwyn;IL;60604;USA
NOTE:Bilingual Real Estate Professional. Scan my postcard for your home value!
END:VCARD`;

  return new NextResponse(vcard, {
    headers: {
      'Content-Type': 'text/vcard',
      'Content-Disposition': 'attachment; filename="Bernardo_Jimenez.vcf"',
    },
  });
}