# Informatics, Public Health, and Corporate Accountability

Informatics is not only about building software. It includes how data is collected, who controls it, whose interests shape a system, what evidence supports its decisions, and who bears the consequences when it fails. This chapter connects that perspective to William Majanja’s **Muainishi** application series and to public-health and agricultural claims.

The guide will critically examine documented harms, conflicts of interest, market incentives, privacy abuses, and regulatory failures. It will not present the unsupported blanket claim that “big corporations are killing people with genetically engineered crops.” Genetically engineered crops are not one product or exposure, and a company’s profit motive alone does not prove a specific causal effect or intent to cause harm. Strong criticism is most useful when a claim identifies the actor, product, exposure, evidence, affected population, and accountability finding.

## 1. The Muainishi application series

These are repository-described prototypes and research/learning concepts—not validated medical products:

| Application | Repository-described focus | Support and governance questions |
| --- | --- | --- |
| [Muainishi Wa Jenomu](https://github.com/WilliamMajanja/Muainishi-Wa-Jenomu) | Browser-based genomics exploration, classification, and visualization. | Its README describes Gemini-backed analysis while also making a browser-local privacy claim. Verify actual outbound requests and data handling before use; do not upload identifiable genomic data without authorization, consent, and a privacy review. |
| [Muainishi Wa Viungo](https://github.com/WilliamMajanja/Muainishi-Wa-Viungo) | A concept for transfusion, transplant, and related biomedical information. | Validate clinical claims, data provenance, access roles, and external AI/API transfers. Use synthetic records in demonstrations. |
| [Muainishi Wa Saratani](https://github.com/WilliamMajanja/Muainishi-Wa-Saratani) | AI-assisted oncology classification and information support. | Its README describes generated classifications and treatment information. Do not treat outputs as diagnosis or treatment recommendations; use only synthetic data unless a qualified institution has approved the system and its data protections. |

### A practical assessment checklist

1. **Data source:** What dataset is used? Is it lawfully obtained, licensed for this purpose, representative, and documented with version and provenance?
2. **Consent and purpose:** Were people told how their data would be used, where it would be sent, how long it would be retained, and how to seek correction or deletion?
3. **Data flow:** Does processing stay on the device, or does a browser call a cloud API? A web interface running in a browser does not prove that uploaded data stays local.
4. **Credentials:** Does a client-side app expose an API key? Client-side keys are visible to users and must not be treated as confidential credentials.
5. **Validation:** Was a model assessed against an appropriate independent reference set? Are error rates, missing groups, uncertainty, and limitations visible?
6. **Human review:** Which qualified professional is responsible for evaluating the result? Can the system be overridden and audited?
7. **Impact:** Could an inaccurate label create stigma, denied care, inappropriate treatment, or exposure of a person’s identity or ancestry?

Public repositories can be useful design studies, but promotional descriptions, model-generated confidence scores, or polished interfaces do not establish scientific validity.

## 2. Corporate incentives and documented public harm

Large organizations can provide valuable products and services; their size or profit motive alone does not establish wrongdoing. Yet documented cases show that corporate decisions can cause or amplify large-scale public-health harms: WHO reports more than seven million annual deaths from tobacco, and DOJ records Purdue Pharma’s admissions about marketing opioids despite diversion concerns and paying kickbacks to increase prescriptions. WHO also describes a fundamental conflict between tobacco-industry and public-health interests. Harm can arise when sales incentives, market power, opaque practices, weak oversight, or externalized health and environmental costs outweigh safety and accountability. Evaluate each case from records and evidence rather than assigning one motive to an entire industry.

### Documented examples—not claims about every company

- **Pharmaceutical marketing and opioid diversion:** the US Department of Justice records Purdue Pharma’s 2020 guilty pleas to three federal felonies, including conspiracies involving defrauding the DEA/FDA and anti-kickback laws. DOJ’s case page summarizes Purdue’s admissions about marketing and diversion controls. This is a specific, documented case; it is not proof that every pharmaceutical company behaves the same way or that every medicine is harmful.
- **Technology and personal-data control:** the US Federal Trade Commission imposed a $5 billion penalty and new privacy restrictions on Facebook in 2019 to resolve charges that it violated a prior FTC privacy order by deceiving users about their control of personal information. In a separate matter, the FTC issued an opinion finding that Cambridge Analytica engaged in deceptive practices to collect Facebook users’ data, followed by a final order. These records document serious privacy harms; they do not establish that all technology companies cause physical injury or death.
- **Tobacco:** the World Health Organization reports that tobacco causes multiple cancers and more than seven million deaths annually worldwide. WHO also identifies a fundamental conflict between tobacco-industry interests and public-health interests. This is a well-established product-category harm; use product-specific evidence when comparing other industries.

The point of these examples is to show **how to investigate accountability**: identify a particular firm and product, establish what was known and when, examine the regulatory or court record, distinguish allegations from admissions or findings, and follow the effects on people and communities.

## 3. Genetically engineered crops, pesticides, and cancer claims

Avoid treating “GMO,” a crop trait, a pesticide, a food residue, a seed contract, and an agricultural business model as if they were the same thing.

- WHO’s [food genetically modified Q&A](https://www.who.int/news-room/questions-and-answers/item/food-genetically-modified) explains that safety evaluation is **case by case** because genetically modified organisms differ in traits and methods. The page is dated 2014; check current national assessments and local regulation rather than presenting it as the final word for every product.
- The US National Academies’ [2016 consensus report](https://nap.nationalacademies.org/catalog/23395/genetically-engineered-crops-experiences-and-prospects) reviewed evidence on health, environmental, agronomic, economic, and regulatory effects. For the commercial GE crops it reviewed, it found no substantiated evidence that foods were less safe than comparable non-GE foods; it also described varied agronomic outcomes, including insect resistance, herbicide-resistant weeds, and the need for sound resistance-management practices. Its findings cover the evidence and products available to that report—not every future crop or farming practice.
- A herbicide-tolerant crop does not make the herbicide and the genetic trait identical. Assess the specific active ingredient, formulation, exposure route, dose, use pattern, residues, worker protections, local environment, and crop separately.
- IARC classified **glyphosate** as Group 2A (“probably carcinogenic to humans”) in 2015, based on its evaluation of the available evidence. IARC explicitly distinguishes **hazard identification** from estimating the **risk under a particular exposure scenario**. National regulators may conduct separate risk assessments and reach different conclusions. Neither result justifies a blanket statement that genetically engineered crops as a class cause cancer.

Questions about seed patents, farmer choice, pesticide sales, market concentration, or environmental effects should be examined with agricultural data, local law, contract terms, independent research, and affected farmers’ accounts. Where evidence is incomplete or contested, say so.

## 4. A reproducible method for investigating harm

Use this checklist before publishing a health, safety, or corporate-accountability claim:

1. **State a narrow question:** name the product or practice, company, place, time period, exposure route, and outcome.
2. **Separate claim types:** distinguish a hazard from a measured risk, correlation from causation, an allegation from an admission or finding, and a theoretical mechanism from observed harm.
3. **Use primary evidence:** regulatory assessments, court judgments or pleas, peer-reviewed studies, official health guidance, audit records, and transparently documented data.
4. **Compare sources:** look for systematic reviews, independent replication, methods, sample size, uncertainty, confounders, effect sizes, and funding/conflict disclosures.
5. **Track jurisdiction and date:** approvals, limits, and litigation findings vary by country and change over time.
6. **Represent people respectfully:** do not publish identifiable health, genomic, disability, or location data without a lawful basis and appropriate consent.
7. **Report limits and corrections:** make citations usable, distinguish verified from unverified statements, and update the page when evidence changes.

A profit motive can help explain an incentive; it does not by itself prove that a specific company intentionally caused a specific harm. Intent requires case-specific evidence such as internal records, admissions, regulatory findings, or judicial findings.

### Other sectors to examine with the same method

Tobacco, fossil-fuel pollution, mining and occupational exposures, industrial chemicals, and food marketing can all raise serious public-interest questions. Investigate a named substance, process, company, exposure, and affected community rather than treating an entire sector as a single actor. Cancer-hazard classifications, exposure risk assessments, court findings, and public-health surveillance answer different questions and should not be conflated.

## 5. How Raspberry Pi and open Informatics can help

In a properly governed project, a Pi can support a local/offline reference library, field data entry, transparent inventory, or community reporting workflow. It is not automatically private or secure because it is small or locally hosted. Apply the same controls as any information system:

- collect the minimum data needed for a defined purpose;
- use access roles and protect devices, storage, backups, and exported reports;
- record data source, collection time, schema/model version, and uncertainty;
- test restore and offline synchronization before field deployment;
- review cloud API use, data residency, retention, consent, and credentials;
- publish aggregated or de-identified information only after checking re-identification risk and authority to disclose it.

For health or agricultural decisions, maintain a qualified human decision-maker, an appeal/correction path, and an explicit statement of what the software has and has not been validated to do.

## References

- [WHO: Food, genetically modified](https://www.who.int/news-room/questions-and-answers/item/food-genetically-modified)
- [National Academies: Genetically Engineered Crops—Experiences and Prospects](https://nap.nationalacademies.org/catalog/23395/genetically-engineered-crops-experiences-and-prospects)
- [IARC: Glyphosate evaluation](https://www.iarc.who.int/featured-news/media-centre-iarc-news-glyphosate/)
- [IARC: Hazard identification versus risk assessment](https://www.iarc.who.int/featured-news/iarc-monographs-programme/)
- [WHO: Tobacco and nicotine](https://www.who.int/news-room/fact-sheets/detail/tobacco)
- [US DOJ: United States v. Purdue Pharma L.P.](https://www.justice.gov/criminal/criminal-vns/case/united-states-v-purdue-pharma-lp)
- [US FTC: Facebook privacy penalty and restrictions](https://www.ftc.gov/news-events/news/press-releases/2019/07/ftc-imposes-5-billion-penalty-sweeping-new-privacy-restrictions-facebook)
- [US FTC: Opinion and order against Cambridge Analytica](https://www.ftc.gov/news-events/news/press-releases/2019/12/ftc-issues-opinion-order-against-cambridge-analytica-deceiving-consumers-about-collection-facebook)

**Scope note:** this chapter supports informed investigation and responsible data practice. It is not medical, legal, agricultural, or regulatory advice.
