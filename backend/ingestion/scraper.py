"""
Scraper module — fetches raw legal text for each topic.
Each topic has a primary URL + BeautifulSoup extraction logic,
and comprehensive fallback text so the demo always works.
"""

import httpx
from bs4 import BeautifulSoup
from typing import Optional
import logging

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}


TOPIC_SOURCES = {
    "pocso": [
        "https://en.wikipedia.org/wiki/Protection_of_Children_from_Sexual_Offences_Act,_2012",
        "https://legislative.gov.in/sites/default/files/A2012-32_0.pdf",
    ],
    "consumer": [
        "https://en.wikipedia.org/wiki/Consumer_Protection_Act,_2019",
        "https://en.wikipedia.org/wiki/Consumer_protection_in_India",
    ],
    "cyber": [
        "https://en.wikipedia.org/wiki/Information_Technology_Act,_2000",
        "https://en.wikipedia.org/wiki/Cyber_crime",
    ],
    "rti": [
        "https://en.wikipedia.org/wiki/Right_to_Information_Act,_2005",
        "https://en.wikipedia.org/wiki/Right_to_information_in_India",
    ],
    "gst": [
        "https://en.wikipedia.org/wiki/Goods_and_Services_Tax_(India)",
        "https://en.wikipedia.org/wiki/GST_(Goods_and_Services_Tax)_in_India",
    ],
}


async def _fetch_url(url: str) -> Optional[str]:
    """Fetch a URL and return the HTML content, or None on failure."""
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url, headers=HEADERS)
            response.raise_for_status()
            return response.text
    except Exception as e:
        logger.warning(f"Failed to fetch {url}: {e}")
        return None


def _extract_wikipedia_text(html: str) -> str:
    """Extract clean text from a Wikipedia article page."""
    soup = BeautifulSoup(html, "lxml")

    for tag in soup.find_all(["script", "style", "sup", "table", "figure"]):
        tag.decompose()

    content_div = soup.find("div", {"id": "mw-content-text"})
    if not content_div:
        content_div = soup.find("div", {"class": "mw-parser-output"})

    if not content_div:
        return ""

    paragraphs = []
    for p in content_div.find_all(["p", "h2", "h3", "li"]):
        text = p.get_text(strip=True)
        if text and len(text) > 20:
            paragraphs.append(text)

    return "\n\n".join(paragraphs)


async def _scrape_topic_from_web(topic_id: str) -> Optional[str]:
    """Try to scrape text from configured URLs for a topic."""
    urls = TOPIC_SOURCES.get(topic_id, [])

    all_text = []
    for url in urls:
        html = await _fetch_url(url)
        if html:
            text = _extract_wikipedia_text(html)
            if text and len(text) > 200:
                all_text.append(text)
                logger.info(f"Scraped {len(text)} chars from {url}")

    if all_text:
        return "\n\n".join(all_text)

    return None


FALLBACK_TEXT = {
    "pocso": """
The Protection of Children from Sexual Offences Act, 2012 (POCSO Act) is a comprehensive law to protect children from offences of sexual assault, sexual harassment, and pornography, while safeguarding the interest of the child at every stage of the judicial process. The Act was enacted by the Parliament of India in 2012 and came into effect on 14 November 2012.

Key Definitions and Scope:
The Act defines a child as any person below the age of 18 years. It is gender-neutral, meaning it protects both male and female children. The Act recognizes various forms of sexual abuse that were not previously defined in Indian law, including penetrative sexual assault, sexual assault, sexual harassment, and using children for pornographic purposes.

Penetrative Sexual Assault (Section 3-4):
Penetrative sexual assault includes insertion of any object into the child's body, or making the child do the same to another person. Aggravated penetrative sexual assault carries higher penalties when committed by police officers, armed forces, public servants, or relatives of the child. The punishment for penetrative sexual assault is imprisonment of not less than 7 years, extendable to imprisonment for life, and a fine. For aggravated penetrative sexual assault, the minimum punishment is 10 years, extendable to imprisonment for life, and a fine.

Sexual Assault (Section 5-6):
Sexual assault involves touching the child's body with sexual intent, or making the child touch another person's body. Aggravated sexual assault occurs when committed by persons in positions of trust or authority. The punishment for sexual assault is imprisonment of not less than 3 years, extendable to 5 years, and a fine. For aggravated sexual assault, the minimum is 5 years, extendable to 7 years, and a fine.

Sexual Harassment (Section 11-12):
Sexual harassment includes showing pornography to a child, making sexual gestures, or stalking a child. The punishment is imprisonment up to 3 years and a fine.

Child Pornography (Section 13-15):
Using a child for pornographic purposes is an offence under the Act. The punishment for using a child for pornographic purposes is imprisonment of up to 5 years and a fine for the first offence, and up to 7 years and a fine for subsequent offences. Storage of pornographic material involving a child is also punishable.

Reporting and Mandatory Reporting (Section 19-22):
Any person who has knowledge that an offence has been committed under this Act is required to report it to the local police or the Special Juvenile Police Unit. Failure to report is punishable with imprisonment of up to 6 months or a fine or both. Media, hotel staff, hospital staff, and other professionals who come in contact with children in their professional capacity have a mandatory duty to report.

Special Courts (Section 28):
The Act provides for the establishment of Special Courts for the trial of offences under the Act. These courts are designed to be child-friendly and to complete the trial within one year from the date of cognizance.

Child-Friendly Procedures (Section 33-38):
The Act lays down child-friendly procedures for recording evidence, including the appointment of a translator or interpreter, the use of video conferencing, frequent breaks during testimony, and ensuring that the child is not confronted by the accused during testimony. The identity of the child is not to be disclosed to the media.

Burden of Proof (Section 29-30):
The Act shifts the burden of proof to the accused. If a person is prosecuted for penetrative sexual assault, sexual assault, or aggravated forms thereof, and the act is proved to have been committed, the Special Court shall presume that the accused committed the offence unless the contrary is proved.

2019 Amendment:
The POCSO Act was amended in 2019 to introduce more stringent punishments, including the death penalty for aggravated penetrative sexual assault of children below 12 years of age. The amendment also increased penalties for other offences under the Act and addressed the issue of child pornography more comprehensively.

Implementation and Challenges:
The National Commission for Protection of Child Rights (NCPCR) monitors the implementation of the Act. Challenges include low conviction rates, delays in trials, lack of awareness among the public, and inadequate infrastructure for child-friendly courts. Many cases go unreported due to stigma and fear.

Key Rights of the Child Under POCSO:
The child has the right to legal representation, the right to be informed about the progress of the case, the right to privacy, the right to compensation, and the right to a child-friendly trial process. The child's statement can be recorded at their residence or a place of their choice.
""",

    "consumer": """
The Consumer Protection Act, 2019 is an Act of the Parliament of India which was enacted to provide for protection and promotion of the interests of consumers. It replaced the older Consumer Protection Act of 1986. The Act received the assent of the President on 9 August 2019 and came into effect on 20 July 2020.

Key Definitions:
A consumer is defined as any person who buys any goods or hires or avails any services for a consideration. It includes offline and online transactions through electronic means, teleshopping, direct selling, or multi-level marketing. The Act covers goods and services purchased or availed through e-commerce platforms.

Consumer Rights (Section 2(9)):
The Act defines six consumer rights: the right to be protected against marketing of goods and services which are hazardous to life and property; the right to be informed about the quality, quantity, potency, purity, standard and price of goods or services; the right to be assured of access to a variety of goods or services at competitive prices; the right to be heard and to be assured that consumers' interests will receive due consideration; the right to seek redressal against unfair trade practices; and the right to consumer awareness.

Central Consumer Protection Authority (CCPA) (Section 10-22):
The Act establishes a Central Consumer Protection Authority (CCPA) to promote, protect, and enforce the rights of consumers. The CCPA has the power to conduct investigations into violations of consumer rights, recall products, order reimbursement of prices, and impose penalties for misleading advertisements. The CCPA can impose a penalty of up to Rs 10 lakh on manufacturers or endorsers for false or misleading advertisements, and up to Rs 50 lakh for subsequent offences.

Consumer Disputes Redressal Commissions (Section 28-73):
The Act provides for a three-tier consumer disputes redressal mechanism: District Consumer Disputes Redressal Commission (for claims up to Rs 1 crore), State Consumer Disputes Redressal Commission (for claims between Rs 1 crore and Rs 10 crore), and National Consumer Disputes Redressal Commission (for claims exceeding Rs 10 crore). Consumers can file complaints electronically.

Product Liability (Section 82-87):
The Act introduces the concept of product liability, making manufacturers, sellers, and service providers liable for any harm caused to consumers due to defective products or deficiency in services. A product liability action can be brought by a complainant against a product manufacturer, product seller, or product service provider.

Mediation (Section 74-81):
The Act provides for mediation as an alternative dispute resolution mechanism. Consumer disputes can be referred to mediation by the Consumer Disputes Redressal Commission at any stage of the complaint. Mediation is to be completed within 3 months, extendable by 2 months.

E-Commerce (Section 2(16)):
The Act covers e-commerce transactions and defines e-commerce as buying or selling of goods or services including digital products over a digital or electronic network. The Consumer Protection (E-Commerce) Rules, 2020 require e-commerce entities to provide information relating to return, refund, exchange, warranty and guarantee, delivery and shipment, modes of payment, and grievance redressal mechanism.

Unfair Trade Practices (Section 2(47)):
Unfair trade practices include false representation about the quality, standard, grade, composition, style, or model of goods or services; publication of misleading advertisements; selling goods or services not complying with standards; hoarding or destruction of goods; and manufacturing spurious goods.

Penalties and Punishments:
The Act provides for imprisonment and fines for various offences. Manufacturing or selling adulterated products can lead to imprisonment up to 6 months and a fine up to Rs 1 lakh for the first offence, and up to 5 years and Rs 5 lakh for subsequent offences. For spurious goods that cause injury, imprisonment can extend to 7 years and a fine up to Rs 5 lakh.

Filing a Consumer Complaint:
A complaint can be filed by a consumer, any recognized consumer association, the Central Government, the State Government, or the Central Authority. The complaint can be filed in writing or electronically. No court fee is required. The complaint must be filed within 2 years from the date on which the cause of action arises.

Key Improvements over 1986 Act:
The 2019 Act introduces product liability provisions, establishes CCPA, covers e-commerce transactions, provides for mediation, allows electronic filing of complaints, and increases pecuniary jurisdiction of Consumer Disputes Redressal Commissions.
""",

    "cyber": """
The Information Technology Act, 2000 (IT Act 2000) is an Act of the Indian Parliament enacted to provide legal recognition for transactions carried out by means of electronic data interchange and other means of electronic communication, commonly referred to as electronic commerce. The Act was substantially amended in 2008 by the Information Technology (Amendment) Act, 2008.

Key Objectives:
The IT Act provides legal recognition to electronic records and digital signatures, establishes a framework for e-governance, defines cyber crimes and prescribes penalties, and provides for the appointment of adjudicating officers and the establishment of the Cyber Appellate Tribunal.

Digital Signatures and Electronic Records (Section 2-10):
The Act gives legal validity to electronic records and digital signatures. Any information rendered or made available in an electronic form, which is accessible so as to be usable for a subsequent reference, is considered an electronic record. Digital signatures using asymmetric crypto systems are given legal recognition.

Cyber Crimes and Penalties:

Tampering with Computer Source Documents (Section 65):
Whoever knowingly or intentionally conceals, destroys, or alters any computer source code used for a computer, computer programme, computer system, or computer network, shall be punishable with imprisonment up to 3 years, or with fine up to Rs 2 lakh, or both.

Hacking with Computer Systems (Section 66):
If any person, dishonestly or fraudulently, does any act referred to in section 43, he shall be punishable with imprisonment up to 3 years or with fine up to Rs 5 lakh or both. Section 43 covers unauthorized access, downloading data, introducing viruses, damaging computers, and disrupting computer systems.

Identity Theft (Section 66C):
Whoever fraudulently or dishonestly makes use of the electronic signature, password, or any other unique identification feature of any other person shall be punished with imprisonment up to 3 years and fine up to Rs 1 lakh.

Cheating by Personation using Computer Resource (Section 66D):
Whoever by means of any communication device or computer resource cheats by personation shall be punished with imprisonment up to 3 years and fine up to Rs 1 lakh.

Cyber Terrorism (Section 66F):
Whoever with the intent to threaten the unity, integrity, security, or sovereignty of India or to strike terror in the people, denies access to any person authorized to access the computer resource, or attempts to penetrate a computer resource without authorization, or introduces any computer contaminant, and by means of such conduct causes or is likely to cause death or injuries or damage to property, shall be punishable with imprisonment which may extend to imprisonment for life.

Publishing or Transmitting Obscene Material (Section 67):
Whoever publishes or transmits obscene material in electronic form shall be punished with imprisonment up to 3 years and fine up to Rs 5 lakh for the first conviction, and imprisonment up to 5 years and fine up to Rs 10 lakh for subsequent convictions.

Child Pornography (Section 67B):
Whoever publishes or transmits material depicting children in sexually explicit acts in electronic form shall be punished with imprisonment up to 5 years and fine up to Rs 10 lakh for the first conviction, and imprisonment up to 7 years and fine up to Rs 10 lakh for subsequent convictions.

Violation of Privacy (Section 66E):
Whoever intentionally or knowingly captures, publishes, or transmits the image of a private area of any person without his or her consent shall be punished with imprisonment up to 3 years or fine not exceeding Rs 2 lakh, or both.

Data Protection and Privacy (Section 43A):
Any body corporate that possesses, deals with, or handles any sensitive personal data or information and is negligent in implementing and maintaining reasonable security practices, resulting in wrongful loss or gain to any person, shall be liable to pay damages by way of compensation to the person so affected.

Intermediary Liability (Section 79):
An intermediary shall not be liable for any third-party information, data, or communication link made available or hosted by the intermediary, provided the intermediary does not initiate the transmission, select the receiver, or modify the information. The intermediary must observe due diligence and follow guidelines prescribed by the Central Government.

Cyber Appellate Tribunal (Section 48-64):
The Act provides for the establishment of a Cyber Appellate Tribunal to hear appeals from the orders of adjudicating officers. Any person aggrieved by an order of the adjudicating officer can file an appeal within 45 days.

Recent Developments:
The IT (Intermediary Guidelines and Digital Media Ethics Code) Rules, 2021 impose additional obligations on social media intermediaries, including the appointment of a Chief Compliance Officer, Nodal Contact Person, and Resident Grievance Officer. Significant social media intermediaries (with more than 5 million registered users) have additional due diligence requirements.

Reporting Cyber Crime:
Cyber crimes can be reported through the National Cyber Crime Reporting Portal (cybercrime.gov.in) or by calling the helpline number 1930. FIRs can be filed at any police station as cyber crime is not location-specific.
""",

    "rti": """
The Right to Information Act, 2005 (RTI Act) is an Act of the Parliament of India which sets out the rules and procedures regarding citizens' right to information. It replaced the former Freedom of Information Act, 2002. The Act came into force on 12 October 2005. The RTI Act is one of the most important transparency laws in India.

Objectives:
The Act aims to promote transparency and accountability in the working of every public authority, to set up a practical regime of right to information for citizens to secure access to information under the control of public authorities, to promote transparency and accountability in government functioning, and to contain corruption and hold governments accountable.

Definition of Information (Section 2(f)):
Information means any material in any form, including records, documents, memos, e-mails, opinions, advices, press releases, circulars, orders, logbooks, contracts, reports, papers, samples, models, data material held in any electronic form and information relating to any private body which can be accessed by a public authority under any other law for the time being in force.

Public Authority (Section 2(h)):
Public authority means any authority or body or institution of self-government established or constituted by or under the Constitution, or by any other law made by Parliament or State Legislature, or by notification issued or order made by the appropriate Government, and includes any body owned, controlled, or substantially financed by funds provided directly or indirectly by the appropriate Government.

Right to Information (Section 3):
Subject to the provisions of this Act, all citizens shall have the right to information. This includes the right to inspection of work, documents, records, taking notes, extracts, or certified copies of documents or records, taking certified samples of material, and obtaining information in the form of diskettes, floppies, tapes, video cassettes, or in any other electronic mode.

How to File an RTI Application (Section 6):
A person who desires to obtain any information under this Act shall make a request in writing or through electronic means in English or Hindi or in the official language of the area, to the Central Public Information Officer or State Public Information Officer specifying the particulars of the information sought. The applicant is not required to give any reason for requesting the information or any other personal details except contact information.

Fee Structure:
The application fee is Rs 10 for Central Government departments. Below poverty line (BPL) applicants are exempted from paying fees. Additional fees may be charged for providing information, such as Rs 2 per page for photocopies.

Time Limits (Section 7):
The Public Information Officer shall provide information within 30 days of receipt of the request. If the information concerns the life or liberty of a person, it shall be provided within 48 hours. If the request is transferred to another public authority, the information shall be provided within 35 days.

Exemptions from Disclosure (Section 8):
The Act provides for certain exemptions from disclosure, including information that would prejudicially affect the sovereignty and integrity of India, security, strategic, scientific, or economic interests of the State, information received in confidence from foreign governments, information that would endanger the life or physical safety of any person, cabinet papers, personal information that has no relationship to any public activity, and trade secrets or intellectual property.

First Appeal (Section 19(1)):
Any person who does not receive a decision within the time specified, or is aggrieved by a decision of the Public Information Officer, may within 30 days from the expiry of such period or from the receipt of such a decision, prefer an appeal to an officer senior in rank to the Public Information Officer.

Second Appeal (Section 19(3)):
A second appeal against the decision of the First Appellate Authority can be filed with the Central Information Commission or the State Information Commission within 90 days.

Central Information Commission (Section 12-14):
The Central Information Commission consists of the Chief Information Commissioner and up to 10 Information Commissioners appointed by the President on the recommendation of a committee consisting of the Prime Minister, the Leader of Opposition in Lok Sabha, and a Union Cabinet Minister nominated by the Prime Minister.

State Information Commission (Section 15-17):
Each State has a State Information Commission consisting of the State Chief Information Commissioner and up to 10 State Information Commissioners appointed by the Governor.

Penalties (Section 20):
If the Central Information Commission or State Information Commission is of the opinion that the Public Information Officer has, without any reasonable cause, refused to receive an application, not furnished information within the time specified, or denied the request for information, it shall impose a penalty of Rs 250 per day until the application is received or information is furnished, subject to a maximum of Rs 25,000. The Commission can also recommend disciplinary action against the officer.

Third Party Information (Section 11):
If an RTI application seeks information relating to or supplied by a third party, the Public Information Officer shall give written notice to the third party within 5 days and give the third party 10 days to make a submission regarding disclosure.

Proactive Disclosure (Section 4):
Every public authority shall maintain all its records duly catalogued and indexed, publish within 120 days of the enactment of this Act the particulars of its organization, functions, duties, powers, directory of officers and employees, monthly remuneration, budget allocated, manner of execution of subsidy programmes, recipients of concessions, permits or authorizations, facilities available to citizens, and other relevant information.

Impact:
The RTI Act has been widely used by citizens, journalists, and activists to uncover corruption, seek accountability, and obtain information from government departments. It has been instrumental in exposing irregularities in government functioning and promoting transparency.
""",

    "gst": """
The Goods and Services Tax (GST) is an indirect tax used in India on the supply of goods and services. It is a comprehensive, multi-stage, destination-based tax that is levied on every value addition. GST was introduced through the 101st Constitution Amendment Act, 2016 and came into effect from 1 July 2017. It replaced multiple cascading taxes levied by the central and state governments.

Types of GST:
There are four types of GST in India: Central GST (CGST) — collected by the Central Government on intra-state supply; State GST (SGST) — collected by the State Government on intra-state supply; Integrated GST (IGST) — collected by the Central Government on inter-state supply; and Union Territory GST (UTGST) — collected on supply in Union Territories without legislature.

GST Registration (Section 22-30):
Every supplier of goods or services or both is required to register under GST if the aggregate turnover in a financial year exceeds Rs 40 lakh (Rs 20 lakh for special category states for goods) or Rs 20 lakh (Rs 10 lakh for special category states for services). Certain persons are required to register regardless of turnover, including persons making inter-state taxable supply, casual taxable persons, persons required to deduct tax at source, input service distributors, e-commerce operators, and persons making taxable supply through e-commerce.

Registration Process:
GST registration can be done online through the GST portal (gst.gov.in). The process involves filling Form GST REG-01 with details such as PAN, mobile number, email address, business details, bank account details, and authorized signatory details. A GSTIN (GST Identification Number) is a unique 15-digit number issued upon registration. The registration certificate is issued in Form GST REG-06 within 7 working days if all documents are in order.

Documents Required for Registration:
PAN card, Aadhaar card, photograph, proof of business registration or incorporation certificate, address proof of place of business (electricity bill, rent agreement, or property tax receipt), bank account statement or cancelled cheque, digital signature, and authorization letter or board resolution for authorized signatory.

GST Tax Rates:
GST rates are structured in five main slabs: 0% (essential items like fresh fruits, vegetables, milk), 5% (items of mass consumption like sugar, tea, edible oil), 12% (processed food, computers), 18% (most goods and services including financial services, telecom), and 28% (luxury items like cars, tobacco, aerated drinks). Some items attract a cess in addition to the 28% rate.

Input Tax Credit (Section 16-21):
Every registered person is entitled to take credit of input tax charged on any supply of goods or services or both to him which are used or intended to be used in the course or furtherance of his business. The input tax credit is available when the person is in possession of a tax invoice, has received the goods or services, the tax charged has been actually paid to the government by the supplier, and the return has been furnished.

GST Returns:
Various returns are required to be filed under GST: GSTR-1 (monthly or quarterly details of outward supplies), GSTR-3B (monthly summary return), GSTR-4 (annual return for composition dealers), GSTR-9 (annual return), and GSTR-9C (reconciliation statement for taxpayers with turnover above Rs 5 crore). Late filing of returns attracts a late fee of Rs 50 per day (Rs 20 per day for nil returns) and interest at 18% per annum on the tax liability.

Composition Scheme (Section 10):
Small taxpayers with aggregate turnover up to Rs 1.5 crore (Rs 75 lakh for special category states) can opt for the composition scheme, under which they pay tax at a lower rate: 1% for manufacturers, 5% for restaurants, and 1% for other suppliers. Composition dealers cannot collect tax from customers, cannot claim input tax credit, and cannot make inter-state supply.

E-Way Bill:
An e-way bill must be generated on the e-way bill portal for movement of goods with a value exceeding Rs 50,000. It is valid for specific distances: 1 day for up to 200 km, and an additional day for every 200 km thereafter. Both the supplier and the transporter can generate the e-way bill.

GST Council:
The GST Council is the key decision-making body for GST in India. It consists of the Union Finance Minister (as Chairman), the Union Minister of State for Revenue, and the Finance Ministers of all States. The Council makes recommendations on GST rates, exemptions, model GST laws, and other matters. Decisions are taken by a three-fourths majority.

Penalties and Offences:
Penalties under GST include a penalty for tax evasion amounting to the tax evaded or Rs 10,000, whichever is higher. For fraudulent availing of input tax credit, the penalty can be up to 100% of the tax amount. Arrest and prosecution provisions exist for tax evasion exceeding Rs 5 crore.

Benefits of GST:
GST eliminates the cascading effect of multiple taxes, creates a unified national market, simplifies the tax structure, reduces tax compliance burden for businesses, increases tax collection for the government, and promotes the formalization of the economy. It also facilitates ease of doing business and reduces logistics costs.

GST Refund:
Refund of GST can be claimed in certain situations such as export of goods or services, supply to SEZ units or developers, excess payment of tax, accumulation of input tax credit due to inverted duty structure, and finalization of provisional assessment. The refund application must be filed within 2 years from the relevant date.
"""
}


async def scrape_topic(topic_id: str) -> str:
    """
    Scrape legal text for a given topic.
    Tries web sources first, falls back to comprehensive built-in text.

    Args:
        topic_id: One of "pocso", "consumer", "cyber", "rti", "gst"

    Returns:
        Raw legal text as a string
    """
    logger.info(f"Scraping topic: {topic_id}")

    web_text = await _scrape_topic_from_web(topic_id)

    if web_text and len(web_text) > 500:
        logger.info(f"Using web-scraped text for {topic_id} ({len(web_text)} chars)")
        return web_text

    fallback = FALLBACK_TEXT.get(topic_id)
    if fallback:
        logger.info(f"Using fallback text for {topic_id} ({len(fallback)} chars)")
        return fallback.strip()

    raise ValueError(f"Unknown topic_id: {topic_id}")


async def scrape_all_topics() -> dict[str, str]:
    """Scrape all 5 topics and return a dict of {topic_id: raw_text}."""
    topics = {}
    for topic_id in TOPIC_SOURCES.keys():
        topics[topic_id] = await scrape_topic(topic_id)
    return topics


TOPIC_NAMES = {
    "pocso": "POCSO Act (Protection of Children from Sexual Offences Act)",
    "consumer": "Consumer Protection Act 2019",
    "cyber": "Cyber Crime Laws (IT Act 2000)",
    "rti": "Right to Information (RTI) Act 2005",
    "gst": "GST Registration",
}
