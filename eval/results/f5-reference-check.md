# F5 reference check

_Verdicts filled in by Claude on 2026-09-30 (one careful LLM reader, not a human). The sheet is all disagreements between the verifier and the reference._

Does the cited source (or another retrieved page of the same opinion) state the sentence? The question's client facts count as given. Write `yes` or `no` after **Your verdict:**.

## R01 `G-C17#0#1`

**Question:** Can owners deduct bed-and-breakfast expenses if they also used the B&B personally?

**Sentence:** This is in accordance with the provisions of section 280A, which disallows deductions for expenses related to the business use of a home if the property is also used personally.

**Source [26 U.S.C. § 280A(e)]**

> (e) Expenses attributable to rental. (1) In general. In any case where a taxpayer who is an individual or an S corporation uses a dwelling unit for personal purposes on any day during the taxable year (whether or not he is treated under this section as using such unit as a residence), the amount deductible under this chapter with respect to expenses attributable to the rental of the unit (or portion thereof) for the taxable year shall not exceed an amount which bears the same relationship to such expenses as the number of days during each year that the unit (or portion thereof) is rented at a fair rental bears to the total number of days during such year that the unit (or portion thereof) is used.
> (2) Exception for deductions otherwise allowable. This subsection shall not apply with respect to deductions which would be allowable under this chapter for the taxable year whether or not such unit (or portion thereof) was rented.

**Your verdict:** no

<details><summary>Verifier / reference</summary>verifier yes (Source 1 section 280A(e) limits deductions for rental expenses based on personal use days, supporting the disallowance principle stated.); reference no (Section 280A(e) only limits rental expenses proportionally for personal use; it does not wholly disallow deductions, and the source doesn't say otherwise.)</details>

---

## R02 `G-S18#0#1`

**Question:** How long does the IRS normally have to assess additional tax after a client files their return?

**Sentence:** If a joint return is made, the IRS has an additional year to assess tax after the filing of such joint return.

**Source [26 U.S.C. § 6013(b)(4)]**

> (4) Additional time for assessment. If a joint return is made under this subsection, the periods of limitations provided in sections 6501 and 6502 on the making of assessments and the beginning of levy or a proceeding in court for collection shall with respect to such return include one year immediately after the date of the filing of such joint return (computed without regard to the provisions of paragraph (3)).

**Your verdict:** no

<details><summary>Verifier / reference</summary>verifier yes (Source 1 states periods of limitations include one year immediately after filing of joint return.); reference no (Source 1 applies only to a joint return made under section 6013(b), the subsection on spouses' joint returns after separate returns; the claim omits this condition.)</details>

---

## R03 `G-X14#0#1`

**Question:** My client is an employee who drives from home to his office in the city every day and wants to deduct the mileage. Is that allowed?

**Sentence:** As an employee, your client cannot deduct the costs of driving from home to his main or regular workplace.

**Source [IRS Pub 463 (2025), p. 20]**

> Example 3. You have no regular office and you don’t have an office in your home. In this case, the location of your first business contact inside the metropolitan area is considered your office. Transportation expenses between your home and this first contact are nondeductible commuting expenses. Transportation expenses between your last business contact and your home are also nondeductible commuting expenses. While you can’t deduct the costs of these trips, you can deduct the costs of going from one client or customer to another. Car Expenses If you use your car for business purposes, you may be able to deduct car expenses. You can generally use one of the two following methods to figure your deductible expenses. • Standard mileage rate. • Actual car expenses. Tip: If you qualify to use both methods, you may want to figure your deduction both ways to see which gives you a larger deduction. The cost of using your car as an employee, whether measured using actual expenses or the standard mileage rate, will no longer be allowed to be claimed as an unreimbursed employee travel expense as a miscellaneous itemized deduction due to the suspension of miscellaneous itemized deductions that are subject to the 2% floor under section 67(a). The suspension applies to tax years beginning after 2017. Deductions for expenses that are deductible in determining adjusted gross income aren’t suspended. For

**Your verdict:** no

<details><summary>Verifier / reference</summary>verifier yes (Source 2 confirms employees cannot deduct commuting expenses and notes employee car expenses are generally not deductible as unreimbursed travel expenses.); reference no (Source 2 doesn't state the home-to-regular-workplace rule; it covers no-regular-office commuting and the suspended employee car deduction, not this claim.)</details>

---

## R04 `G-C14#0#3`

**Question:** Will the Tax Court estimate a client's business expenses under the Cohan rule if the client kept records but didn't produce proof of payment?

**Sentence:** The Cohan rule does not apply if the taxpayer could have and should have maintained the necessary records for the claimed deductions.

**Source [T.C. Memo. 2024-95, at *18]**

> We are thus faced with a situation where, other than the Table Expenses, the record lacks evidence of the outlays underlying petitioners’ Schedule C and E expenses. As noted above, the Cohan doctrine allows us to estimate acknowledged expenses that a taxpayer cannot fully substantiate. Petitioners invoke our discretion to make an estimate. Respondent argues we lack discretion because there exists no evidentiary basis upon which to make an estimate. See Vanicek, 85 T.C. at 743. Petitioners’ specific circumstances, however, give us grounds to decline to rely on Cohan to estimate the amounts of their deductible expenses that they failed to substantiate. As the U.S. Court of Appeals for the Second Circuit observed in Cohan v. Commissioner, 39 F.2d at 543, not only did the taxpayer in that case fail to keep account of his travel expenses; he “probably could not have done so.” “That observation,” we have said, “suggests a limit on Cohan’s scope, under which estimating unsubstantiated expenses would be inappropriate when proper recordkeeping is feasible and can reasonably be expected.” Joseph v. Commissioner, T.C. Memo. 2020-65, at *40–41. “In fact,” we added, “the Court of Appeals for the Seventh Circuit has recognized just such a limitation, identifying a trend under which Cohan, ‘while not * * * repudiate[d] * * * entirely, is * * * not invoke[d] * * * where the claimed but unsubstantiated deductions are of a sort for which the taxpayer could have and should have maintained the necessary records.’” Id. (quoting Lerch v. Commissioner, 877 F.2d 624, 628 (7th Cir. 1989), aff’g T.C. Memo. 1987-295).

**Your verdict:** no

<details><summary>Verifier / reference</summary>verifier yes (Source 2 recognizes Cohan limitation where proper recordkeeping feasible and reasonably expected.); reference no (Source 2 describes a limit on Cohan's scope that the Court may invoke (discretionary), not an absolute rule; the claim overstates it as categorical.)</details>

---

## R05 `G-X05#0#3`

**Question:** My client has run a horse boarding and breeding operation for eight years with only one profitable year. Does the presumption help, and how does the Tax Court usually decide these cases?

**Sentence:** The Tax Court has found that a lack of consistent profits over many years, despite efforts to improve profitability, can indicate that the activity is not engaged in for profit.

**Source [T.C. Memo. 2013-294, at *17-19]**

> watch them grow. However, running a large-scale breeding operation takes many
> hours of hard work, and Mrs. Jary-Mathis has sacrificed family and personal
> time to promote her horses. This factor weighs slightly against a profit motive.
> J. Conclusion
> After weighing all the facts and circumstances in light of the relevant
> factors, we conclude that petitioners did not engage in their cutting horse activity
> with the requisite profit objective. Mrs. Jary-Mathis is determined to be a
> successful horsewoman. She wants to build a reputation as a producer of top-level
> cutting horses. However, she has pursued this goal independently of any desire to
> earn profits. She has continued training and breeding cutting horses for 17 years
> without ever approaching profitability, yet she has never seriously considered
> discontinuing operations. Accordingly, we sustain respondent's determination
> that petitioners did not engage in the cutting horse activity for profit.
> III. Accuracy-Related Penalties
> Respondent determined that petitioners were liable for an accuracy-related
> penalty pursuant to section 6662(a) for each of the tax years at issue. Section
> 6662(a) and (b)(1) and (2) imposes a penalty of 20% on any underpayment
> attributable to, among other things, (1) negligence or disregard of rules or
> regulations; or (2) any substantial understatement of income tax. An
> understatement is substantial if it exceeds the greater of $5,000 or 10% of the
> income tax required to be shown on the return for the taxable year. Sec.
> The Commissioner bears the burden of production with respect to this
> penalty. Sec. 7491©. The Commissioner satisfies the burden by presenting
> sufficient evidence supporting the relevant penalty. Higbee v. Commissioner, 116
> T.C. 438, 446 (2001). Respondent determined that petitioners underpaid their
> 2008, respectively. These amounts exceed the "substantial understatement"
> threshold for each year in question. Thus, respondent has carried his burden of
> demonstrating that petitioners substantially understated their income tax.

**Your verdict:** no

<details><summary>Verifier / reference</summary>verifier yes (Source 4 example shows Tax Court found lack of profitability despite long-term operation indicates no profit motive.); reference no (Source 4 shows 17 years without profit, but it says nothing about efforts to improve profitability; it found she pursued her goals independently of profit.)</details>

---

## R06 `G-S06#0#2`

**Question:** How much can a business deduct for gifts to one customer in a year?

**Sentence:** The limit is applicable regardless of the number of gifts made to that recipient.

**Source [26 CFR 1.274-3(f)-(g)]**

> (f) Special rules —(1) Partnership. In the case of a gift by a partnership, the $25 annual limitation contained in paragraph (a) of this section shall apply to the partnership as well as to each member of the partnership. Thus, in the case of a gift made by a partner with respect to the business of the partnership, the $25 limitation will be applied at the partnership level as well as at the level of the individual partner. Consequently, deductions for gifts made with respect to partnership business will not exceed $25 annually for each recipient, regardless of the number of partners.
> (2) Husband and wife. For purposes of applying the $25 annual limitation contained in paragraph (a) of this section, a husband and wife shall be treated as one taxpayer. Thus, in the case of gifts to an individual by a husband and wife, the spouses will be treated as one donor; and they are limited to a deduction of $25 annually for each recipient. This rule applies regardless of whether the husband and wife file a joint return or whether the husband and wife make separate gifts to an individual with respect to separate businesses. Since the term taxpayer in paragraph (a) of this section refers only to the donor of a gift, this special rule does not apply to treat a husband and wife as one individual where each is a recipient of a gift. See paragraph (e)(1) of this section.
> (g) Cross reference. For rules with respect to whether this section or § 1.274-2 applies, see § 1.274-2(b)(1) (iii).

**Your verdict:** no

<details><summary>Verifier / reference</summary>verifier yes (Source 2(f)(1) states deductions 'will not exceed $25 annually for each recipient, regardless of the number of partners,' supporting the principle regardless of number.); reference no (Source 2 says regardless of number of partners, not number of gifts to a recipient; it doesn't state this.)</details>

---

## R07 `G-S24#0#0`

**Question:** Can a client claim miscellaneous itemized deductions, like unreimbursed employee expenses, on a 2024 return?

**Sentence:** For tax years beginning after 2017, taxpayers can no longer claim any miscellaneous itemized deductions that are subject to the 2%-of-AGI limitation, including unreimbursed employee expenses.

**Source [IRS Pub 17 (2025), p. 103]**

> 12. Other Itemized Deductions What’s New Standard mileage rate. The 2025 rate for business use of a vehicle is 70 cents a mile. Reminders No miscellaneous itemized deductions allowed. You can no longer claim any miscellaneous itemized deductions. Miscellaneous itemized deductions are those deductions that would have been subject to the 2%-of-adjusted-gross-income (AGI) limitation. See Miscellaneous Itemized Deductions, later. Fines and penalties. Rules regarding deducting fines and penalties have changed. See Fines and Penalties, later. Introduction This chapter explains that you can no longer claim any miscellaneous itemized deductions, unless you fall into one of the qualified categories of employment claiming a deduction relating to unreimbursed employee expenses. Misthose cellaneous deductions that would have been subject to the 2%-of-AGI limitation. You can still claim certain expenses as itemized deductions on Schedule A (Form 1040) or Schedule A (Form 1040-NR), or as an adjustment to income on Form 1040 or 1040-SR. This chapter covers the following topics. itemized deductions are • Miscellaneous itemized deductions. • Expenses you can’t deduct. • Expenses you can deduct. • How to report your deductions. You must keep records to verify your deductions. You should keep receipts, canceled checks, substitute checks, financial account statements, and other documentary evidence. For more information on recordkeeping, see What Records Should I Keep? in chapter 1. Useful Items You may want to see: Publication 463 463 Travel, Gift, and Car

**Your verdict:** no

<details><summary>Verifier / reference</summary>verifier yes (Source 1 states taxpayers can no longer claim miscellaneous itemized deductions subject to 2%-of-AGI limitation, including unreimbursed employee expenses.); reference no (Source 1 says no misc deductions allowed but doesn't mention 'tax years beginning after 2017' and notes qualified-employment exceptions, so 'including unreimbursed employee expenses' is overstated.)</details>

---

## R08 `G-X27#0#0`

**Question:** My client is an off-duty police officer paid directly by businesses to provide security. Is that income subject to self-employment tax?

**Sentence:** Self-employment tax is imposed on self-employment income, which consists of gross income derived by an individual from any trade or business carried on by the individual.

**Source [26 U.S.C. § 1402(b)]**

> (b) Self-employment income. The term “self-employment income” means the net earnings from self-employment derived by an individual (other than a nonresident alien individual, except as provided by an agreement under section 233 of the Social Security Act) during any taxable year; except that such term shall not include— (1) in the case of the tax imposed by section 1401(a), that part of the net earnings from self-employment which is in excess of (i) an amount equal to the contribution and benefit base (as determined under section 230 of the Social Security Act) which is effective for the calendar year in which such taxable year begins, minus (ii) the amount of the wages paid to such individual during such taxable years; or
> (2) the net earnings from self-employment, if such net earnings for the taxable year are less than $400.
> For purposes of paragraph (1), the term “wages” (A) includes such remuneration paid to an employee for services included under an agreement entered into pursuant to the provisions of section 3121(l) (relating to coverage of citizens of the United States who are employees of foreign affiliates of American employers), as would be wages under section 3121(a) if such services constituted employment under section 3121(b), and (B) includes compensation which is subject to the tax imposed by section 3201 or 3211. An individual who is not a citizen of the United States but who is a resident of the Commonwealth of Puerto Rico, the Virgin Islands, Guam, or American Samoa shall not, for purposes of this chapter be considered to be a nonresident alien individual. In the case of church employee income, the special rules of subsection (j)(2) shall apply for purposes of paragraph (2).

**Your verdict:** no

<details><summary>Verifier / reference</summary>verifier yes (Source 1 states self-employment tax is imposed on self-employment income derived from any trade or business.); reference no (Source 1 defines self-employment income as net earnings, with exceptions; the 'gross income from any trade or business' language is in Source 5 (§1402(a)), not Source 1.)</details>

---

## R09 `G-X24#0#0`

**Question:** My client rents out a California house but also stays there regularly. Can he deduct the rental expenses on Schedule E?

**Sentence:** The amount of rental expenses that can be deducted is limited if the dwelling unit is considered a home due to personal use.

**Source [IRS Pub 527 (2025), p. 25]**

> . . . . . . . . . . . . . . . . . . . . . . . . . $1,241 85 91 . . . . . . . . Net rental income for house . . . . . . . . . . . 1,417 $3,694 You use Schedule E, Part I, to report your rental income and expenses. You enter your income, expenses, and depreciation for the house in the column for Property A. Because all property was placed in service this year, you must use Form 4562 to figure the depreciation. See the instructions for Form 4562 for more information on preparing the form. Personal Use of Dwelling Unit (Including Vacation Home) If you have any personal use of a dwelling unit (including a vacation home) that you rent, you must divide your expenses between rental use and personal use. In general, your rental expenses will be no more than your total expenses multiplied by a fraction, the denominator of which is the total number of days the dwelling unit is used and the numerator of which is the total number of days actually rented at a fair rental price. Only your rental expenses may be deducted on Schedule E (Form 1040). Some of your personal expenses may be deductible on Schedule A (Form 1040) if you itemize your deductions.

**Your verdict:** yes

<details><summary>Verifier / reference</summary>verifier yes (Source 1 states rental expenses are limited if dwelling unit has personal use.); reference no (Source 1 says expenses must be divided for any personal use; it doesn't say the limit applies only if the unit is considered a home.)</details>

---

## R10 `G-X30#0#0`

**Question:** My client's partnership claimed a conservation easement deduction at $10 million, but the IRS values it at $3 million. What penalty applies?

**Sentence:** The claimed value of the conservation easement exceeds the correct value by more than 200%, which constitutes a gross valuation misstatement.

**Source [T.C. Memo. 2026-45, at *33]**

> misstatement. § 6662(a), (b)(3). A misstatement is “substantial” if the value of the property claimed on a return equals or exceeds 150% of the correct amount. § 6662(e)(1)(A). The penalty increases to 40% in the case of a “gross valuation misstatement,” which occurs when the claimed value equals or exceeds 200% of the correct value. § 6662(h)(2)(A)(i).
> RRP claimed a charitable contribution deduction of $12,765,000 for the conservation easement on its 2017 return. We have determined that the easement’s fair market value on the valuation date was $649,955. The claimed value therefore exceeded 1,900% of the correct value, constituting a gross valuation misstatement within the meaning of section 6662(h).
> Section 6664(c)(1) generally provides that no accuracy-related penalty shall apply if the taxpayer demonstrates reasonable cause and good faith. However, that defense is unavailable for gross valuation misstatements attributable charitable deduction property. § 6664(c)(3). Accordingly, the 40% gross valuation misstatement penalty applies to the portion of RRP’s underpayment attributable to the overvaluation of the conservation easement.
> to
> On the basis of the Court’s valuation determination in RRP’s case, gross valuation misstatement penalties also apply to the portions of the Yosts’ underpayments attributable to the overvaluation of the conservation easement.
> To reflect the foregoing,
> Decisions will be entered under Rule 155.

**Your verdict:** yes

<details><summary>Verifier / reference</summary>verifier yes (Source 2 defines gross valuation misstatement as claimed value equaling or exceeding 200% of correct value.); reference no (Source 2 says gross misstatement occurs at 200% or more of correct value, but the claim says the client's value exceeds 200%; the $10M vs $3M facts are not in the source (that's ~333%, though).)</details>

---

## R11 `G-S23#0#2`

**Question:** A self-employed client wants to deduct groceries and household bills as business costs. Is that allowed?

**Sentence:** Therefore, groceries and household bills cannot be deducted as business costs.

**Source [T.C. Memo. 2023-128, at *14]**

> III. Home Office Deductions
> Generally, the expenses of maintaining a household, including amounts paid for rent, water, utilities, and the like, are not deductible. Treas. Reg. § 1.262-1(b)(3). Section 280A(a) provides that “no deduction otherwise allowable under this chapter shall be allowed with respect to the use of a dwelling unit which is used by the taxpayer during the taxable year as a residence.” If, however, a portion of the residence is used as a place of business, a share of the expenses properly attributable to the portion of the property used for the business may be deductible as a business expense, subject to the rules of section 280A. § 280A(c).
> No deduction is allowed with respect to a home office unless “allocable to a portion of the dwelling unit which is exclusively used on a regular basis” as the taxpayer’s principal place of business. § 280A(a),
> 7 Respondent argues, in the alternative, that even if petitioner intended to earn a profit from Ovium, his expenses should be amortized as startup expenses. See §§ 195(a), (b), and (c)(1), 162(a); Jackson v. Commissioner, 86 T.C. 492, 514 (1986) (finding no deduction under section 162 unless related to an ongoing business), aff’d, 864 F.2d 1521 (10th Cir. 1989). We need not address this argument because, as explained above, we find that petitioner did not conduct the Ovium activity for profit; therefore, petitioner’s expenses are not eligible for amortization as section 195 startup expenses. See § 195(b)(1), (c)(1)(A) (providing amortization is allowed only for expenses that are incurred to create new trade or business); Commissioner v. Groetzinger, 480 U.S. at 35 (finding that a profit motive is required to have a trade or business); Wilmot v. Commissioner, T.C. Memo. 2011-293 (finding amortization under section 195 need not be addressed where activity is not conducted for a profit).

**Your verdict:** yes

<details><summary>Verifier / reference</summary>verifier yes (Follows logically from claim 0: household expenses are not deductible, so groceries and bills cannot be deducted.); reference no (Source doesn't address groceries; conclusion that they categorically can't be deducted goes beyond the household-expense rule and home-office exception.)</details>

---

## R12 `G-X18#0#4`

**Question:** My client earned a $60,000 sales commission, but the payer kept $40,000 of it to cancel rent she owed him. How much income does she have?

**Sentence:** Here, the fact that the rent owed was paid out of the commission is irrelevant; the client realized $60,000 of income as commission income.

**Source [T.C. Memo. 2001-252, at *7-9]**

> action against Mr. Riccardi.
> Mr. Riccardi paid petitioner an additional $6,000 on August
> 13, 1996. After the Aspen Road property was sold, and Mr. Riccardi
> agreed to pay petitioner’s moving expenses, petitioner agreed to
> vacate the property. Nothing in the record indicates that
> petitioner took any action to compel Mr. Riccardi to pay her the
> $40,500 balance of the commission or that petitioner contested the
> matter. Nor is there any evidence that Mr. Riccardi took any
> action to compel petitioner to pay additional expenses he may have
> incurred because of petitioner’s failure to pay rent. The dispute
> as to the amount of the remaining debt petitioner owed to Mr.
> Riccardi and the remaining amount of commission Mr. Riccardi owed
> petitioner apparently was resolved and settled by the end of 1996.
> Petitioner was obligated under the written lease to pay Mr.
> Riccardi $1,800 per month from January 1, 1995, to December 31,
> 1996, for a total of $43,200 for the 24-month period. Although
> petitioner occupied the property and owed rent for the entire 24-
> month term of the lease, she paid Mr. Riccardi only $5,701.68.
> Thus, when she vacated the property at the end of 1996, she owed
> Mr. Riccardi $37,498.32 of unpaid rent ($43,200 - $5,701.68).
> Additionally, because petitioner failed to pay the rent when it was
> due, Mr. Riccardi incurred more than $3,000 of additional interest
> expense and costs for which petitioner was liable under the lease.
> Consequently, petitioner owed Mr. Riccardi at least $40,500 by the
> end of 1996.
> Petitioner earned a commission of $60,500 on the sale of the
> shopping center in 1996. The M. Riccardi Agency paid petitioner
> $20,000. The $40,500 balance owed to petitioner was credited
> against the $40,500 debt petitioner owed to Mr. Riccardi in 1996.
> To conclude, we hold that petitioner realized $60,500 of income as
> commission income in 1996.

**Source [T.C. Memo. 2001-252, at *5-6]**

> property for sale. Mr. Riccardi sold the Aspen Road property
> before the end of 1996. Petitioner was required to vacate the
> Aspen Road property before settlement on the sale of the house.
> She moved out of the property by the end of the year, after Mr.
> Riccardi agreed to pay her moving expenses. As a result of
> petitioner’s failure to pay the monthly rent on the Aspen Road
> property, Mr. Riccardi incurred more than $3,000 of additional
> interest expenses and other costs. In January 1997, Mr. Riccardi
> paid $5,998.50 of petitioner’s moving expenses.
> The M. Riccardi Agency issued a Form 1099-Misc, Miscellaneous
> Income, to petitioner reporting $60,500 of nonemployee compensation
> in 1996. In addition to the commission on the sale of the shopping
> center, petitioner earned $6,199 in wages and $14 of interest.
> Petitioner did not file a Federal income tax return for 1996.
> Respondent issued a notice of deficiency to petitioner based on
> Forms 1099 and W-2, Wage and Tax Statement, and other documents
> received from third parties reflecting their payments to petitioner
> in 1996.
> OPINION
> Petitioner does not contest respondent’s determinations as set
> forth in the notice of deficiency, including the additions to tax,
> except for $40,500 of the $60,500 reflected in a Form 1099 issued
> to petitioner by the M. Riccardi Agency and used by respondent in
> his determination of petitioner’s income. Respondent contends that
> petitioner had $40,500 of income in 1996 either from the discharge
> of indebtedness she owed Mr. Riccardi or by the constructive
> receipt of the commission on the sale of the shopping center. We
> agree with respondent.
> Section 61(a) defines “gross income” broadly, and specifically
> includes both “compensation for services” and “income from
> discharge of indebtedness” within its meaning. It is well settled
> that where an employee owes a debt to the employer, crediting the

**Source [T.C. Memo. 2001-252, at *6-7]**

> that where an employee owes a debt to the employer, crediting the
> salary earned by the employee against the employee’s debt to the
> employer, without any cash changing hands, is income to the
> employee. See, e.g., Newmark v. Commissioner, 311 F.2d 913, 915
> (2d Cir. 1962) (citing Old Colony Trust Co. v. Commissioner, 279
> U.S. 716, 729 (1929)), affg. T.C. Memo. 1961-285; Tucker v.
> Commissioner, 69 T.C. 675 (1978); Cox v. Commissioner, T.C. Memo.
> 1996-241; Phillips v. Commissioner, T.C. Memo. 1993-514; Kelley v.
> Commissioner, T.C. Memo. 1991-324, affd. without published opinion
> 988 F.2d 1218 (11th Cir. 1993); Lehew v. Commissioner, T.C. Memo.
> 1987-389; Evans v. Commissioner, T.C. Memo. 1980-103; sec. 1.61-
> 12(a), Income Tax Regs.
> Here, the fact that the rent petitioner owed Mr. Riccardi was
> paid out of the commission the M. Riccardi Agency owed petitioner
> is irrelevant. See Tucker v. Commissioner, supra at 678.
> Receiving compensation in the form of cash is not a prerequisite to
> the receipt of taxable income. Id. at 679 (citing Cohen v.
> Commissioner, 63 T.C. 267, 283 (1974), affd. per curiam 543 F.2d
> 725 (9th Cir. 1976)). When petitioner’s debt to Mr. Riccardi was
> satisfied, petitioner received an immediate economic benefit equal
> to the amount of the debt used to satisfy the delinquent rental
> obligation. See id.
> Petitioner contends that the offset of the rent she owed to
> Mr. Riccardi was not income because she disputed the amount she
> owed to Mr. Riccardi. On March 29, 1996, when Mr. Riccardi paid
> petitioner $14,000 of the $60,500 commission, he told her that the
> $46,500 balance was offset by expenses he had incurred with respect
> to the Aspen Road property. Although petitioner may have disagreed
> with Mr. Riccardi as to the amount she owed at that time, she
> continued to occupy the house without paying rent and took no
> action against Mr. Riccardi.

**Source [T.C. Memo. 2001-252, at *4-5]**

> Aspen Road property and listed it for sale. Petitioner paid $1,000
> in March, $701.68 in May, and $1,000 in June 1995.
> In May or June 1995, petitioner listed a shopping center for
> sale with the M. Riccardi Agency. Mr. Riccardi thought he would be
> able to recover the expenses he had incurred for the Aspen Road
> property from petitioner’s share of the commission on the sale of
> the shopping center. Therefore, he took the Aspen Road property
> off the market. Petitioner paid $1,000 of rent in each of the
> months of July, August, and November 1995. She did not pay any
> rent in 1996.
> Mr. Riccardi kept a log of the money he spent on the Aspen
> Road property, including the downpayment on the purchase price,
> closing costs, mortgage payments, taxes, costs associated with his
> attempts to sell the property, and maintenance and repair costs.
> The log shows that by the end of March 1996, the total expenses
> exceeded the $5,701.68 of rent petitioner had paid by $22,300.
> The shopping center sold in 1996; it was the only property
> petitioner sold for Mr. Riccardi in 1996. The Riccardi Agency
> received its $121,000 commission on March 28, 1996. Mr. Riccardi
> allocated one-half ($60,500) of the commission to petitioner as her
> share. Mr. Riccardi paid petitioner $14,000 on March 29, 1996. At
> that time he told her that $46,500 of the balance of her commission
> would be retained by him and used to offset the expenses he had
> incurred in excess of the rent petitioner had paid and the $20,000
> profit he expected from the Aspen Road Property. He paid
> petitioner an additional $6,000 on August 13, 1996.
> In May or June 1996, Mr. Riccardi again listed the Aspen Road
> property for sale. Mr. Riccardi sold the Aspen Road property

**Your verdict:** yes

<details><summary>Verifier / reference</summary>verifier no (Sources cite $60,500 commission, not $60,000. Claim amounts differ from source facts.); reference yes (Source 4 says payment from the commission is irrelevant; Source 2 held the full commission was income, and the $60,000 figure applies that holding to the client.)</details>

---

## R13 `G-X19#0#1`

**Question:** A supervisor approved the accuracy-related penalties on my client's conservation easement deduction in writing, but only after the penalties were first communicated to the client, though before assessment. The case is appealable to the Eleventh Circuit. Is the approval timely?

**Sentence:** In this case, the supervisor's approval occurred after the penalties were communicated to the client but before the assessment.

**Source [T.C. Memo. 2023-5, at *15]**

> The written supervisory approval is not required to take any specific form. See Palmolive Bldg. Invs., LLC v. Commissioner, 152 T.C. 75, 85–86 (2019). But it generally must be obtained no later than (1) the date on which the IRS issues the deficiency notice, or (2) the date, if earlier, on which the IRS formally communicates to the taxpayer the Examination Division’s determination to assert a penalty. See Belair Woods, LLC v. Commissioner, 154 T.C. 1, 15 (2020).
> In Kroner v. Commissioner, 48 F.4th 1272 (11th Cir. 2022), rev’g in part T.C. Memo. 2020-73, the U.S. Court of Appeals for the Eleventh Circuit disagreed with the Tax Court regarding the timing of the section 6751(b) approval requirement. The Eleventh Circuit concluded that “the IRS satisfies [s]ection 6751(b) so long as a supervisor approves an initial determination of a penalty assessment before it assesses those penalties.” Id. at 1276.
> In Laidlaw’s Harley Davidson Sales, Inc. v. Commissioner, 29 F.4th 1066, 1071 (9th Cir. 2022), rev’g and remanding 154 T.C. 68 (2020), the U.S. Court of Appeals for the Ninth Circuit considered the timeline for obtaining supervisory approval of “assessable penalties,” which are not subject to deficiency procedures. The Ninth Circuit held that, for an assessable penalty, supervisory approval is timely if secured before the penalty is assessed or “before the relevant supervisor loses discretion whether to approve the penalty assessment.” Id. at 1074.
> We follow the relevant precedent of the Court of Appeals to which an appeal would generally lie. See Golsen v. Commissioner, 54 T.C. 742, 757 (1970), aff’d, 445 F.2d 985 (10th Cir. 1971). In this case the appeal would lie in the Ninth Circuit, which has not addressed this issue in a deficiency case. Because the immediate supervisor’s signature on the 30-day letter is timely under either standard, the Court does not address the potential conflict.

**Your verdict:** yes

<details><summary>Verifier / reference</summary>verifier yes (Source 1 references the facts as stated in the case context regarding approval timing relative to client communication and assessment.); reference no (This is the user's hypothetical fact; Source 1 concerns a 30-day letter signed by the supervisor, not post-communication approval.)</details>

---

## R14 `G-C05#0#2`

**Question:** Tax Court jurisdiction section 7436 worker classification additions to tax penalties

**Sentence:** The Tax Court's jurisdiction includes determining the applicability of any penalty or addition to tax for which the partnership may be liable under the relevant subchapter.

**Source [26 U.S.C. § 6234(a)-(c)]**

> (a) In general. Within 90 days after the date on which a notice of a final partnership adjustment is mailed under section 6231 with respect to any partnership taxable year, the partnership may file a petition for a readjustment for such taxable year with— (1) the Tax Court,
> (2) the district court of the United States for the district in which the partnership’s principal place of business is located, or
> (3) the Court of Federal Claims.
> (b) Jurisdictional requirement for bringing action in district court or Court of Federal Claims. (1) In general. A readjustment petition under this section may be filed in a district court of the United States or the Court of Federal Claims only if the partnership filing the petition deposits with the Secretary, on or before the date the petition is filed, the amount of (as of the date of the filing of the petition) the imputed underpayment, penalties, additions to tax, and additional amounts with respect to such imputed underpayment if the partnership adjustment was made as provided by the notice of final partnership adjustment. The court may by order provide that the jurisdictional requirements of this paragraph are satisfied where there has been a good faith attempt to satisfy such requirement and any shortfall of the amount required to be deposited is timely corrected.
> (2) Interest payable. Any amount deposited under paragraph (1), while deposited, shall not be treated as a payment of tax for purposes of this title (other than chapter 67).
> (c) Scope of judicial review. A court with which a petition is filed in accordance with this section shall have jurisdiction to determine all partnership-related items for the partnership taxable year to which the notice of final partnership adjustment relates, the proper allocation of such items among the partners, and the applicability of any penalty, addition to tax, or additional amount for which the partnership may be liable under this subchapter.

**Your verdict:** yes

<details><summary>Verifier / reference</summary>verifier yes (Source 1 section 6234(c) explicitly grants jurisdiction over penalty applicability.); reference no (§6234(c) gives courts, including the Tax Court, this scope in partnership adjustment proceedings; the claim omits that context and implies it applies generally.)</details>

---

## R15 `G-S07#0#2`

**Question:** My self-employed consultant client took an 18-month engagement in another city. Can they deduct their travel expenses while away from home?

**Sentence:** Since the client took an 18-month engagement, the travel expenses may be subject to the limitations outlined in section 274 if the travel involved substantial nonbusiness activity.

**Source [26 U.S.C. § 274(c)-(d)]**

> (c) Certain foreign travel. (1) In general. In the case of any individual who travels outside the United States away from home in pursuit of a trade or business or in pursuit of an activity described in section 212, no deduction shall be allowed under section 162 or section 212 for that portion of the expenses of such travel otherwise allowable under such section which, under regulations prescribed by the Secretary, is not allocable to such trade or business or to such activity.
> (2) Exception. Paragraph (1) shall not apply to the expenses of any travel outside the United States away from home if— (A) such travel does not exceed one week, or
> (B) the portion of the time of travel outside the United States away from home which is not attributable to the pursuit of the taxpayer’s trade or business or an activity described in section 212 is less than 25 percent of the total time on such travel.
> (3) Domestic travel excluded. For purposes of this subsection, travel outside the United States does not include any travel from one point in the United States to another point in the United States.
> (d) Substantiation required. No deduction or credit shall be allowed— (1) under section 162 or 212 for any traveling expense (including meals and lodging while away from home),
> (2) for any expense for gifts, or
> (3) with respect to any listed property (as defined in section 280F(d)(4)),
> unless the taxpayer substantiates by adequate records or by sufficient evidence corroborating the taxpayer’s own statement (A) the amount of such expense or other item, (B) the time and place of the travel or the date and description of the gift, (C) the business purpose of the expense or other item, and (D) the business relationship to the taxpayer of the person receiving the benefit. The Secretary may by regulations provide that some or all of the requirements of the preceding sentence shall not apply in the case of an expense which does not exceed an amount prescribed pursuant to such regulations. This subsection shall not apply to any qualified nonpersonal use vehicle (as defined in subsection (i)).

**Your verdict:** no

<details><summary>Verifier / reference</summary>verifier yes (Source 2 § 274(c)(1) allows restrictions on deductions for travel with nonbusiness activity portions.); reference no (Source 2's limits apply only to travel outside the US; claim omits that condition, and the 18-month duration isn't tied to it.)</details>

---

## R16 `G-S05#0#3`

**Question:** business meals deduction 50 percent limitation food and beverages

**Sentence:** The deduction limitation applies to business meals unless an exception applies under section 274(e).

**Source [26 U.S.C. § 274(k)-(l)]**

> (k) Business meals. (1) In general. No deduction shall be allowed under this chapter for the expense of any food or beverages unless— (A) such expense is not lavish or extravagant under the circumstances, and
> (B) the taxpayer (or an employee of the taxpayer) is present at the furnishing of such food or beverages.
> (2) Exceptions. Paragraph (1) shall not apply to— (A) any expense described in paragraph (2), (3), (4), (7), (8), or (9) of subsection (e), and
> (B) any other expense to the extent provided in regulations.
> (l) Transportation and commuting benefits. No deduction shall be allowed under this chapter for any expense incurred for providing any transportation, or any payment or reimbursement, to an employee of the taxpayer in connection with travel between the employee’s residence and place of employment, except as necessary for ensuring the safety of the employee.

**Your verdict:** no

<details><summary>Verifier / reference</summary>verifier yes (Source 4 section 274(k)-(l) references exceptions under subsection (e), supporting the claim.); reference no (Source 4 covers 274(k) lavishness and presence requirements with 274(e) exceptions, not the 50% limitation, which is in 274(n).)</details>

---

## R17 `G-X13#0#3`

**Question:** My client lost the receipts for last year's business travel but is sure she spent about $6,000. Can the court estimate the deduction?

**Sentence:** Without any substantiation or evidence of the lost receipts, the court is unlikely to allow an estimate of the travel expenses.

**Source [T.C. Memo. 2023-26, at *7]**

> adequate substantiation of the items on [the taxpayer’s] returns”), petitioner’s documents, bank statements, and canceled checks clearly substantiate certain business expenses petitioner’s accounting practice incurred during the 2017 tax year. Specifically, petitioner’s USAA checking account records indicate expenses of $500, $120, and $1,295, corresponding to a payment made to the Public Company Accounting Oversight Board, a CPA license fee paid to the California Board of Accountancy, and a payment to Drake Software (a provider of tax preparation software), respectively. Accordingly, we conclude that petitioner is entitled to a deduction for each of these three expenses (namely the $500, $120, and $1,295 described above) pursuant to section 162.
> Despite this finding petitioner neither testified to, nor produced any documents or receipts into the record that provide, detail or insight into the remainder of the business expenses he reported. Although under Cohan we may estimate additional expenses not subject to section 274(d), because of the limited record any basis on which an estimate may be made is lacking. See Williams, 245 F.2d at 560; Cohan v. Commissioner, 39 F.2d at 543–44; Vanicek, 85 T.C. at 742–43. Because the record contains no evidence upon which we could base such an estimate, we find that petitioner has failed to prove that he is entitled to any deductions in excess of what we have allowed under section 162(a). See Rule 142(a). Consequently, we sustain respondent’s disallowance of petitioner’s claimed deductions in excess of the three above-mentioned expenses we find petitioner is entitled to deduct.
> B.
> Travel Expense Deduction

**Your verdict:** no

<details><summary>Verifier / reference</summary>verifier yes (Source 3 states lack of evidence prevents estimating expenses; no basis for estimate without substantiation.); reference no (Source 3 concerns non-274(d) business expenses lacking any evidence; the travel expense section is not shown, so claim about travel isn't supported.)</details>

---

## R18 `G-X27#0#2`

**Question:** My client is an off-duty police officer paid directly by businesses to provide security. Is that income subject to self-employment tax?

**Sentence:** The self-employment tax does not apply to compensation paid to an employee.

**Source [26 U.S.C. § 1402(c)(1)]**

> (c) Trade or business. The term “trade or business”, when used with reference to self-employment income or net earnings from self-employment, shall have the same meaning as when used in section 162 (relating to trade or business expenses), except that such term shall not include— (1) the performance of the functions of a public office, other than the functions of a public office of a State or a political subdivision thereof with respect to fees received in any period in which the functions are performed in a position compensated solely on a fee basis and in which such functions are not covered under an agreement entered into by such State and the Commissioner of Social Security pursuant to section 218 of the Social Security Act;

**Your verdict:** no

<details><summary>Verifier / reference</summary>verifier yes (Source 2 states self-employment tax does not apply to compensation paid to an employee.); reference no (Source 2 (§1402(c)(1)) concerns public office exclusion; the employee compensation rule is §1402(c)(2), not stated in Source 2.)</details>

---

## R19 `G-X29#0#2`

**Question:** My client signed joint returns, and her husband's business deductions were later disallowed. She had no involvement in the business. Can she be relieved of the tax?

**Sentence:** In the case of Thurman L. Phemister, the court found that the requesting spouse had no involvement with the business and did not know about the unallowable deductions, which supported her claim for relief.

**Source [T.C. Memo. 2009-201, at *41-42]**

> and (d), respondent must prove that Ms . Ross had actual knowledg e
> "( . . .continued) knowledge at the time she signed the returns of the items giving rise to those deficiencies . See Hopkins v . Commissioner , 121 T .C . 73, 83-86 (2003) ; sec . 1 .6015-3(d)(5), Example (5), Income Tax Regs . 26Accuracy-related penalties under sec . 6662 are allocated to the individual whose activity generated the penalty . Sec . 1 .6015-3(d)(4)(iv)(B), Income Tax Regs . .'Accordingly, Ms . Ross cannot avoid liability for the penalties arising from petitioners' horse activity .
> of the unallowable deductions when she signed the returns . Sec .
> 6015(c)(3)(C) . Respondent did not do so .
> In Sowards v . Commissioner , T .C . Memo . 2003-180, the
> taxpayer sought relief from liabilities arising from
> unsubstantiated deductions her husband claimed with respect t o
> his legal practice . We found, as we do here, that th e
> Commissioner failed to prove that-the requesting spousei!had
> actual knowledge that the other spouse's business deductions were
> not allowable . Like the taxpayer in Sowards , Ms . Ross had no
> involvement with Dr . Phemister's ER physician business .
> .She did
> not know who kept his books and records, and there is no evidence
> she reviewed any of .his claimed deductions . She knew only that
> he supplied his business' books and records to an accountant who
> used them to prepare petitioners' returns .
> On this record we conclude that respondent has not prove n
> 27Respondent does not argue that Ms . Ross does'not qualify

**Source [T.C. Memo. 2009-201, at *31-33]**

> (C) the other individual filing the joint return establishes that in signing the return he or she did not know, and had no reason to know, that there was such understatement ;
> (D) taking into account all of the facts and circumstances, it is inequitable to hold the other individual liable for th e deficiency in tax for such taxable year attributable to such understatement ; an d
> (E) the other individual elects (in such
> form as the Secretary may prescribe) the benefits of this subsection not later than the date which is 2 years after the date the Secretary has begun collection activities with respect to the individual making the election ,
> then the other individual shall-be relieved of liability-for tax (including interest, penalties, and other amounts) for such taxable year to the extent such liability is attributable to such understatement .
> 16 1 f a spouse requests relief under sec . 6015(c), the Commissioner bears the burden of proving that assets have bee n (continued .
> . .) In order . to make relief from joint and several liabilit y
> more accessible, Congress repealed section 6013(e) and enacted ,
> "( .
> ., .continued)
> transferred between former spouses as part of a fraudulent scheme and that the spouse requesting relief had actual knowledge of a deficiency . Sec . 6015(c)(2), (3) (A) (ii) , (C) .
> "Respondent does not assert that Ms . Ross is not qualified
> for relief with respect to understatements of tax attributable to any other items of income,, deduction, or credit on the joint returns .
> (D) of section 6015(b)(1), and with respect to the ER physician
> business, we interpret respondent's argument to be an assertion
> that Ms . Ross . has not met the requirements of subparagraphs (C)
> and (D) .18
> Petitioners' deficiencies are partly attributable to their .

**Your verdict:** no

<details><summary>Verifier / reference</summary>verifier yes (Source 2 states Ms. Ross had no involvement with business and did not know of unallowable deductions; Source 4 confirms respondent did not prove actual knowledge.); reference no (Sources show no involvement and no actual knowledge, but under 6015(c) burden on Commissioner; not a finding of 'did not know' under (b), though close. Overstates.)</details>

---

## R20 `G-X02#0#2`

**Question:** My client lives in Iowa, doesn't farm, and received Conservation Reserve Program payments in 2006 on land he owns. Are those payments subject to self-employment tax?

**Sentence:** A taxpayer may conduct their trade or business personally or through an agent, and if they do not materially participate in farming activities, the payments received are not included in determining net earnings from self-employment.

**Source [140 T.C. No. 16, at *21-23]**

> participating in the CRP and managing his CRP properties with the primary intent
> of making a profit.
> Petitioner contends that his actual participation in the CRP and his work
> complying with the CRP contract requirements were de minimis and did not
> constitute farming. He n aintains that all physical labdf necessary to pladt, seed,
> weed, mow, and maintain the properties (propeity maintenance activities) in
> accordance with the C
> contraàts via(cid:0)541performed by his contractor and should
> not be attributed to him. It is irnmaterial, hov ever, that the property maintenance
> activities were carried o t by someone other than petitioner. As noted supra, for
> purposes of section 1402 a taxpayer'may conduct his trade or businèss personally
> or through an agent. Sec. 1.1402(a)-2(b), Income Tax Regs.; Rev. Rul. 60-32,
> 1960-1 C.B. 23 (stating that similar payments made to individuals under the Soil
> Bank Act v/ere includible in the individual's net earnings from self-employment if
> the individual operated his farm either personally or through agents or
> employees).19 A taxpayer who hires another "to render the services necessary to
> fulfill'' the taxpayer's obligations under a contract is nonetheless liable for self-
> employment tax with respect to the income the taxpayer receives pursuant to that
> at *6.
> Payments and benefits attributable to the acreage reserve
> program are includible in determining the recipient's net earnings from self-employment if he operates his farm personally or through agents or employees. .This is also true if his farm is operated by others and he participates materially in the production of commodities, or management of such production, within the meaning of section 1402(a)(1) * * *. * * * If he does not so operate or materially participate, payments received are not to be included in determining net earnings from self-employment.
> As a participant in the CRP,,petitioner, either,directly or through>Mr. Redlin
> as his agent,

**Source [140 T.C. No. 16, at *1-2]**

> During 2006 and 2007 P-H received payments under the U.S.
> Department of Agriculture Conservation Reserve Program (CRP) Respondent detern ined that P.-H was liable for self-employment tax under I.R.C. sec. 1401 on the CRP payments. P-H claims that the CRP payments are ot includible in his self-employment income because he was nei her engaged in nor derived the CRP payments from operation of a trade or business. Alternatively, P-H claims that the CRP paym,ents are excluded from the calculation of his net earnings.from self-employment under I.R.C..sec. 1402(a)(1) because the CRP payments constituted "rentals from real estate".
> Held: P-H's CRP payments are includible in his selfemployment inco e under I.R.C. sec. 1401 because he was engaged in a trade or busin ss during the years in issue and there was a nexus between his trade cr business 'and the CRP payments he received.
> Held, further, P-H's CRP payments are not "rentals from real
> estate" within the meaning of I.R.C. sec. 1402(a)(1). Wuebker v. Commissioner, 110 T.C. 431 (1998), rev'd, 205 F.3d 897 (6th Cir. 2000), is overruled.
> Paul J. Quast and Neal J. Shapiro, for petitioners.
> Blaine C. Holiday, for respondent.
> respondent determined deficiencies with respect to petitioners' Federal income tax
> of $3,341 and $3,664 for 2006 and 2007, respectively. After concessions,' the
> sole issue for decision is whether petitioners are liable for self-employment tax
> under section 14012 on payments they received under the U.S. Department of
> Agriculture (USDA) Conservation Reserve Program (CRP).
> 'On their 2006 Schedule E, Supplemental Income and Loss, petitioners reported that they paid management fees of $2,001 with respect to property in Grant County, South Dakota, that Rollin J. Morehouse owned. See infra p. 3: Petitioners concede that their tax return preparer erroneously entered $2,001 and that they actually paid management fees of $201 with respect to the property.

**Source [140 T.C. No. 16, at *42-43]**

> activities with respect to the property were not those usually rendered in
> connection with the rental of property).
> . Although the CRP statute, the regulations, and the contracts refer to the ,
> payments as rental payments, we do not find that the use of the term "rental"
> dictates a conclusion that the payments constituted-"rentals from real estate". S_ee
> eg, Wuebker v. Commissioner, 205 F.3d at 904 (noting that Congress qualified
> the use of the term "rent" with respect to CRP payments by providiñg that the CRP
> payments would be made "in the form of rental payments"). We are not required
> to treat as rental payments all payments labeled "rent". Instead we may examine
> the substance of so-called rent payments to decide whether the payments actually
> constituted rent or some other type of income. See Opine Timber Co. v.
> F.2d 368 (5th Cir. 1977). The CRP payments petitioner received appear to be
> proceeds from his own use of the land rather than rent he received for permitting
> another entity to use his land. See, e.g., Webster Corp. v. Commissioner, 25 T.C.
> Memo. 1970-179 (holding that conservation reserve program payments "are in the
> nature of receipts from fárm operations in that they replace income which
> producers could have expected to realize from the normal use of the land devoted
> to the program"); Rev. Rul. 60-32, supra. Such a conclusion is consistent with our
> holding that the "rentals from real estate" exception should be narrowly construed.
> Johnson v. Commissioner, 60 T.C. at 833.
> We hold that the CRP payments at issue do not constitute "rentals from real
> estate" within the meaniiig of seòtion 1402(a)(1) and are not excluded from the
> calculation of petitioner's net earnings from self-employment for 2006 and 2007.
> In so doing, we overrule bur holding in Wuebker v. Commissioner, 110 T.C. 431.

**Source [140 T.C. No. 16, at *30-31]**

> 108, supra, explained that it had previously issued an announcement,
> tax treatment of payments made.by the USDA under land diversion programs in
> 22In deciding whether a full-time gambler who made wagers solely for his
> own account was engaged in a trade or business for Federal income tax purposes, the Suprème Court in Commissioner v. Groetzinger, 480 U.S. 23, 27 n.7 (1987), stated as follows: "Judge Friendly some time ago observed that 'the courts have properly assumed that the term [trade or business] includes all means of gaining a livelihood by work, even those which would scarcely be so characterized in common speech.' Trent v. Commissioner, 291 F.2d 669, 671 (CA2 1961)." (Emphasis added.)
> The concept of work that the term "trade or business" embodies is incorporated into the CRP contracts, which impose meaningful obligations and duties on petitioner that he had to perform with continuity and regularity in order to receive the CRP payments.
> which.it stated that a farraer»who receives cash or a,payment in kind from the
> USDA for participation in.a lánd diversion program is liable for. self-employment
> tax on the payments,,á coríclusion that was consistent with guidance provided in
> . Rev. Rul. 60-32, supra, with respect to two earlier land diversion programs. The
> IRS also noted, however, that Rev. Rul. 60-32, supra; states that participants in
> land diversion programs are not subject to self-employment tax on.the payments if
> the participants do not operate a farm or·materially participate in the farming
> activities. The IRS expleined that the conclusion in Rev. Rul.·60-32, supra, is
> relevant only with respect to the exception from net income from self-employment
> provided in section 1402'a)(1) for-"rentals from real estate". It cited with approval
> and relied on the opinion of the U.S. Court of Appeals for the Sixth Circuit in
> Wuebker v. Commissiòner, 205 F.3d 897, for the proposition that CRP payments

**Source [140 T.C. No. 16, at *31-32]**

> Wuebker v. Commissiòner, 205 F.3d 897, for the proposition that CRP payments
> do not fall within the ren al income exclusion but pointed out that the taxpayer in
> Wuebker was engaged in the business of farming when he received the CRP
> payments. Because the I1S had received questions regarding whether CRP
> payments received by a recipient who is retired or not otherwise actively engaged
> in farming are subject to self-employment tax, it issued the proposed revenue
> ruling to respond to those questions.
> that CRP rental-payments (including incentive payments) from the USDA to (1)
> "a farmer actively engaged in the trade or business of farming.who enrolls land in
> CRP and fulfills the CRP contractual obligations personally" (taxpayer A) and'(2)
> "an individual not otherwise actively engaged in the trade or business of farming
> for a third party to perform the required activities" (taxpayer B) are both includible
> in net income from self-employment and are not excluded from net income from
> self-employment as "rentals from real estate" under section 1402(a)(1). The IRS
> explained the holdings of the proposed revenue procedure as follows:

**Source [140 T.C. No. 16, at *29-30]**

> during his participation in the CRP in finding that the CRP payments were
> includible.in his self-employment income. However, we do not read R__ay to make
> the taxpayer's engagement in the business of farming before enrolling property.in
> the CRP determinative of whether CRP payments constitute income from self-
> employment.
> 'A taxpaye is not required to have prior experience in a particular
> trade or business to be permitted deductions under section 162; what is required is
> that the taxpayer.have commenced an activity that qualifies as a trade or business.
> Goodwin v. Commissioner, 75 T.C. at 433.
> Like the taxpayers in Bot v. Commissioner, 1.18 T.C. 138, petitioner was an
> active participant in a payment program (in this case the CRP)·who regularly and
> continuously maintained his status as a participant, maintained the eligibility
> status of his properties, made decisions regarding.how to satisfy his obligations
> under the CRP contracts, including hiring Mr. Redlin, entering into the 1999
> Roberts County CRP, removing a portion of the Grant County pròperty from the
> CRP, and participatmg m the emergency haying programs, and he engaged in such
> activities for prbfit. Furt1ermore, becatise the receipt of CRP payments depended
> on petitioner's continued maintenance of his land in accordance with the CRP
> contracts, his participation in the CRP was not merely a passivé in(cid:0)570estment
> Whether petitioner's acti
> ities withiespect to the CRP constituted farming or
> simply continuous and regular participation in an activity for profit, we are
> convinced that petitioner was engaged in a trade or business as.defmed by section
> b.
> Notice 2006-108
> contained a proposèd revenue ruling regarding whether CRP payments were
> includible in net income from self-ernployment for purposes of calculating a
> taxpayer's liability for self-employment tax, and solicited comments cpncerning
> the conclusions reached in the proposed revenue ruling. The IRS in Notice 2006-
> 108, supra, explained that it had previously issued an announcement,

**Source [140 T.C. No. 16, at *43-44]**

> In so doing, we overrule bur holding in Wuebker v. Commissioner, 110 T.C. 431.
> We sustain respondent's determination that the CRP payments petitioner
> received in 2006 and 2007 must be included in the calculation of his net earnings
> from self-employment.urider section 1401 and hence are subject to self-
> employment tax. The CRP payments are not excluded from this calculation by
> virtue of section 1402(a)(1) because the CRP payments do not constitute "rentals
> from real estate". Because we find that the CRP payments are not "rentals from
> real estate", we need not each the issue of whether the CRP payments constituted
> includible farm income.
> We have considered all of the parties' arguments. To the extent not
> discussed above, we find those arguments to be irrelevant, moot, or without merit.
> To reflect the foregoing,
> Decision will be entered under
> Rule 155.
> Reviewed by the.Court.
> PARIS, J., did not participate in the consideration of this opinion.

**Your verdict:** no

<details><summary>Verifier / reference</summary>verifier no (Sources state non-farmers may still owe self-employment tax on CRP if engaged in trade or business; contradicts second part of claim.); reference yes (Source 3 cites the regulation on acting through an agent and Rev. Rul. 60-32 on non-participation excluding payments.)</details>

---

## R21 `G-X29#0#4`

**Question:** My client signed joint returns, and her husband's business deductions were later disallowed. She had no involvement in the business. Can she be relieved of the tax?

**Sentence:** Since your client had no involvement in her husband's business, she may be able to establish that she did not know and had no reason to know of the disallowed deductions, which is a key requirement for relief under section 6015(b).

**Source [26 U.S.C. § 6015(b)]**

> (b) Procedures for relief from liability applicable to all joint filers. (1) In general. Under procedures prescribed by the Secretary, if— (A) a joint return has been made for a taxable year;
> (B) on such return there is an understatement of tax attributable to erroneous items of one individual filing the joint return;
> (C) the other individual filing the joint return establishes that in signing the return he or she did not know, and had no reason to know, that there was such understatement;
> (D) taking into account all the facts and circumstances, it is inequitable to hold the other individual liable for the deficiency in tax for such taxable year attributable to such understatement; and
> (E) the other individual elects (in such form as the Secretary may prescribe) the benefits of this subsection not later than the date which is 2 years after the date the Secretary has begun collection activities with respect to the individual making the election,
> then the other individual shall be relieved of liability for tax (including interest, penalties, and other amounts) for such taxable year to the extent such liability is attributable to such understatement.
> (2) Apportionment of relief. If an individual who, but for paragraph (1)(C), would be relieved of liability under paragraph (1), establishes that in signing the return such individual did not know, and had no reason to know, the extent of such understatement, then such individual shall be relieved of liability for tax (including interest, penalties, and other amounts) for such taxable year to the extent that such liability is attributable to the portion of such understatement of which such individual did not know and had no reason to know.
> (3) Understatement. For purposes of this subsection, the term “understatement” has the meaning given to such term by section 6662(d)(2)(A).

**Your verdict:** yes

<details><summary>Verifier / reference</summary>verifier no (Lacks knowledge is necessary but insufficient; Source 1 also requires inequitability (D) and timely election (E).); reference yes (Source 1 makes lack of knowledge/reason to know a requirement; hedged 'may be able' inference from non-involvement is reasonable.)</details>

---

## R22 `G-X12#0#1`

**Question:** My client's partnership filed its Tax Court petition a few days after the 90-day deadline following a final partnership adjustment. Does the court lose jurisdiction?

**Sentence:** The Tax Court has held that the filing of a petition in a TEFRA case involves several timing issues that have been held to be jurisdictional, but the 90-day deadline in I.R.C. § 6234(a) is not one of them.

**Source [167 T.C. No. 11, at *8]**

> the equitable tolling doctrine to apply.’” Arellano v. McDonough, 143 S. Ct. 543, 548 (2023) (alteration in original) (quoting United States v. Brockamp, 519 U.S. 347, 350 (1997)). When considering this question, the Supreme Court has considered the text and structure of the statute that establishes the deadline. See Enbridge Energy, LP v. Nessel ex rel. Michigan, 146 S. Ct. 1074, 1082–83 (2026).
> Our Court has also considered this question. In North Wall Holdings, LLC v. Commissioner, 165 T.C. 143 (2025), we held that deadlines to file a TEFRA petition were jurisdictional. In so holding, we noted that the filing of a petition in a TEFRA case involves several timing issues that have been held to be jurisdictional. See id. at 155–58. A petition can be filed only after a final partnership administrative adjustment (FPAA) is issued by the Commissioner; only the TMP can file a petition during the initial 90 days after the Commissioner mails an FPAA; and notice partners can file a petition during the subsequent 60 days. Id. We further highlighted that, for 40 years, both Congress and the courts have treated the TEFRA petition deadline as jurisdictional, see id. at 157–59, including as recently as 2022, see SNJ Ltd. v. Commissioner, 28 F.4th 936 (9th Cir. 2022).

**Your verdict:** no

<details><summary>Verifier / reference</summary>verifier yes (Source 2 states TEFRA timing issues are jurisdictional but distinguishes the 90-day I.R.C. § 6234(a) deadline as not jurisdictional.); reference no (Source 2 discusses TEFRA deadlines as jurisdictional but says nothing about § 6234(a) not being one of them.)</details>

---

## R23 `G-S03#0#2`

**Question:** Can a home office deduction create a loss if the business earns very little income?

**Sentence:** If a taxpayer does not conduct the business activity for profit, the expenses, including home office deductions, are not deductible.

**Source [T.C. Memo. 2023-128, at *14]**

> III. Home Office Deductions
> Generally, the expenses of maintaining a household, including amounts paid for rent, water, utilities, and the like, are not deductible. Treas. Reg. § 1.262-1(b)(3). Section 280A(a) provides that “no deduction otherwise allowable under this chapter shall be allowed with respect to the use of a dwelling unit which is used by the taxpayer during the taxable year as a residence.” If, however, a portion of the residence is used as a place of business, a share of the expenses properly attributable to the portion of the property used for the business may be deductible as a business expense, subject to the rules of section 280A. § 280A(c).
> No deduction is allowed with respect to a home office unless “allocable to a portion of the dwelling unit which is exclusively used on a regular basis” as the taxpayer’s principal place of business. § 280A(a),
> 7 Respondent argues, in the alternative, that even if petitioner intended to earn a profit from Ovium, his expenses should be amortized as startup expenses. See §§ 195(a), (b), and (c)(1), 162(a); Jackson v. Commissioner, 86 T.C. 492, 514 (1986) (finding no deduction under section 162 unless related to an ongoing business), aff’d, 864 F.2d 1521 (10th Cir. 1989). We need not address this argument because, as explained above, we find that petitioner did not conduct the Ovium activity for profit; therefore, petitioner’s expenses are not eligible for amortization as section 195 startup expenses. See § 195(b)(1), (c)(1)(A) (providing amortization is allowed only for expenses that are incurred to create new trade or business); Commissioner v. Groetzinger, 480 U.S. at 35 (finding that a profit motive is required to have a trade or business); Wilmot v. Commissioner, T.C. Memo. 2011-293 (finding amortization under section 195 need not be addressed where activity is not conducted for a profit).

**Your verdict:** no

<details><summary>Verifier / reference</summary>verifier yes (Source 1 states no deduction allowed if activity not conducted for profit.); reference no (Source 1 only says startup amortization is unavailable without profit motive; it does not say home office deductions are barred.)</details>

---

## R24 `G-C13#0#5`

**Question:** Are a farmer's heavy-duty pickup trucks subject to the strict substantiation rules for listed property?

**Sentence:** Taxpayers must demonstrate that their heavy-duty pickup trucks are modified in a way that they are not likely to be used more than a de minimis amount for personal purposes to avoid strict substantiation requirements.

**Source [T.C. Memo. 2022-117, at *18-19]**

> Respondent argues that the depreciation and other deductions claimed in connection with petitioners’ pickup trucks and other vehicles are subject to the strict substantiation requirements of section 274(d). Petitioners argue that section 274(d) is inapplicable to the pickup trucks because each was modified in some way to be used on the farm and was not likely to be used more than a de minimis amount for personal purposes. With respect to the 1995 Ford F250 and the 1999 Ford F350, the Court agrees. The 1995 Ford F250 had a bale stabber attached and was used exclusively to transport hay, and the 1999 Ford F350 was equipped with tools and equipment, including a torch, oil, and two 60gallon fuel tanks. The Court finds that both were modified with the result that they were not likely to be used more than a de minimis amount for personal purposes and that the strict substantiation requirements of section 274(d) do not apply with respect to those two trucks.
> The 2008 Ford F350 and the 2011 Ford F350 were both one-ton diesel engines that petitioners used to transport livestock between farms, to the veterinarian, or to market. Petitioners kept trailers
> attached to both trucks at nearly all times, including a 24-foot flatbed and a 30-foot livestock trailer for transporting livestock to the veterinarian in the case of an emergency. On the basis of petitioners’ credible testimony, as well as the weight and function of the vehicles and the attached trailers, the Court finds that strict substantiation requirements of section 274(d) do not apply with respect to the 2008 Ford F350 and the 2011 Ford F350.

**Source [T.C. Memo. 2022-117, at *18]**

> Section 274(d)(4) provides that no deduction shall be allowed “with respect to any listed property (as defined in section 280F(d)(4))” unless the taxpayer substantiates “by adequate records or by sufficient evidence corroborating the taxpayer’s own statement.” Listed property includes, among other things, any passenger automobile or any other property used as a means of transportation. § 280F(d)(4)(A)(i) and (ii). The flush text of section 274(d), however, excludes from the strict substantiation requirements any “qualified nonpersonal use vehicle.” A “qualified nonpersonal use vehicle” is “any vehicle which, by reason of its nature, is not likely to be used more than a de minimis amount for personal purposes.” § 274(i). The strict substantiation requirements of section 274(d) generally apply to any pickup truck or van “unless the truck or van has been specially modified with the result that it is not likely to be used more than a de minimis amount for personal purposes.” Treas. Reg. § 1.274-5(k)(7). Other qualified nonpersonal use vehicles not subject to the strict substantiation requirements of section 274(d) include several relevant categories. Those include any vehicle designed to carry cargo with a loaded gross vehicle weight over 14,000 pounds, combines, flatbed trucks, and tractors and other special purpose farm vehicles. Treas. Reg. § 1.274-5(k)(2)(ii)(C), (F), (J), (Q). Respondent has previously conceded additional depreciation of $5,228 for each year with respect to a combine and an additional section 179 deduction of $9,800 with respect to a flatbed trailer for 2013.

**Source [T.C. Memo. 2022-117, at *33]**

> 
> The Court held supra that the strict substantiation requirements of section 274(d) are not applicable to the 1995 Ford F250, the 1999 Ford F350, which served as Mr. Hoakison’s tool truck, the 2008 Ford F350, or the 2011 Ford F350. Petitioners have demonstrated the business use and purpose of those vehicles, and the payments to State Farm and the Union County Treasurer with respect to those vehicles will be allowed as deductions. The strict substantiation requirements are applicable to the 1999 Dodge Dakota, however, and petitioners have not satisfied those requirements. They have not provided sufficient substantiation of the business use of the vehicle. Accordingly, those deductions will not be allowed. Similarly, petitioners have not introduced any information regarding the use of the 1992 Chevy S10, and respondent’s disallowance of a deduction for the insurance payment for that vehicle is also sustained.
> With respect to the payments to Farmers Mutual, petitioners introduced into evidence pages from a 2015 invoice showing $1,492 due and bank records showing payment of the invoice. The invoice lists several vehicles and other equipment covered by the policy, but petitioners have not introduced any additional evidence connecting those items with the farming operation or, in the case of the vehicles, have not satisfied the requirements of section 274(d). On the basis of the invoice and petitioners’ other records, the Court will allow an additional deduction of $36, representing the premiums paid for equipment designated on the invoice as “Farm Use Only.” The remaining amounts paid to EMC and Farmers Mutual are disallowed.

**Your verdict:** yes

<details><summary>Verifier / reference</summary>verifier yes (Sources 3 and 1 establish that taxpayers must demonstrate trucks are modified to avoid personal use to escape substantiation requirements.); reference no (Sources say general rule applies unless specially modified; Court also relied on weight, function, trailers, not only modification; 'must demonstrate' is overstated.)</details>

---

## R25 `G-C19#0#3`

**Question:** When evaluating an offer in compromise from a cannabis business, can the IRS ignore expenses that section 280E makes nondeductible?

**Sentence:** The IRS can ignore expenses that section 280E makes nondeductible when evaluating an offer in compromise from a cannabis business, as this policy is consistent with the congressional intent underlying section 280E and the discretion granted to the Commissioner to set guidelines for offers-in-compromise.

**Source [165 T.C. No. 13, at *5-6]**

> Because Mission’s reasonable collection potential substantially exceeded Mission’s outstanding liability, the revenue officer and his supervisor made a preliminary decision to reject Mission’s April 2022 offer-in-compromise. They determined that Mission had “the ability to pay [its] liability in full” and that its “special circumstances did not warrant hardship.” That preliminary decision was then forwarded to Appeals for consideration in conjunction with Mission’s challenge to the Commissioner’s collection activity.
> Mission had a collection hearing after the preliminary decision to reject its offer-in-compromise. During that hearing, Mission informed the settlement officer that it was aware of the preliminary decision to reject its offer-in-compromise. Mission stated that it did not agree with the Commissioner’s policy that operating expenses for a cannabis business should be disallowed for the purpose of calculating reasonable collection potential, and it expressed its intent to challenge the policy in court. Mission did not discuss other collection alternatives during the hearing.
> 4 At the time the revenue officer computed Mission’s reasonable collection potential, he determined there were 113 months left until the expiration of the collection period of limitations for Mission’s liabilities. See IRM 5.8.5.25(3).
> The settlement officer sustained the rejection of the offer-in-
> compromise.
> The Commissioner
> issued two Notices of Determination sustaining the Notices of Intent to Levy. The two Notices of Determination provided the same explanation for rejecting Mission’s offer-in-compromise, concluding that “[t]he revenue officer did not allow all other operating expenses per Section 280e [sic] – you are involved in cannabis business, which is considered an illegal business activity for federal purposes.”

**Source [165 T.C. No. 13, at *8-9]**

> IV. Review of Appeals’ Determination
> The Commissioner’s two Notices of Determination provided the same reason for rejecting the offer-in-compromise. The notices stated: “The revenue officer did not allow all other operating expenses per Section 280e [sic] – you are involved in cannabis business, which is considered an illegal business activity for federal purposes.”
> Section 280E provides that no deduction is allowed for amounts paid in carrying on any trade or business if such business consists of trafficking in controlled substances which is prohibited by state or federal law. I.R.C. § 280E. Federal law characterizes marijuana as a Schedule I controlled substance. See Comprehensive Drug Abuse Prevention and Control Act of 1970, Pub. L. No. 91-513, § 202(c), 84 Stat. 1236, 1249 (codified as amended at 21 U.S.C. § 812(c) (2012)); Olive, 139 T.C. at 21. Although the dispensing of medical marijuana is legal under California law, it remained illegal under federal law during the years the underlying liabilities arose, when the offer-in-compromise was made, and when the offer-in-compromise was evaluated. See Olive, 139 T.C. at 39. Even if the trafficking business is legal under state law, being illegal under federal law results in the application of section 280E. Olive, 139 T.C. at 39.
> The question presented here is the extent to which section 280E may be taken into account in the computation of a taxpayer’s reasonable collection potential. There are two plausible readings of the Commissioner’s reliance on section 280E. We address both.

**Source [165 T.C. No. 13, at *9-10]**

> One plausible reading is that the revenue officer and the reviewing settlement officer rejected the offer-in-compromise because they thought section 280E required the disallowance of business expenses in a marijuana business when calculating the reasonable collection potential. But section 280E addresses deductions and credits, not the computation of reasonable collection potential. It is found in subtitle A, which relates to income tax, subchapter B, which relates to the computation of taxable income, and part IX, which identifies items that are not deductible. Of course, the location or grouping of Code sections is not to be given legal effect. See I.R.C. § 7806(b). But the text of section 261, the first Code section in part IX, makes clear that the provisions in that part relate to computing taxable income, providing: “In computing taxable income no deduction shall in any case be allowed in respect of the items specified in this part.” (Emphasis added.) And the text of section 280E makes clear that it applies to deductions and credits, providing: “No deduction or credit shall be allowed for any amount paid or incurred during the taxable year in carrying on any trade or business . . . of trafficking in controlled substances . . . .” (Emphasis added.) Simply stated, section 280E disallows deductions or credits for any amount paid or incurred in carrying on the trade or business of trafficking in controlled substances; it does not address what expenses may or may not be considered for the purpose of calculating a taxpayer’s reasonable collection potential. Accordingly, rejecting the offer-in-
> compromise solely on the basis of an understanding that section 280E required that result would have been an error.

**Source [165 T.C. No. 13, at *9]**

> The question presented here is the extent to which section 280E may be taken into account in the computation of a taxpayer’s reasonable collection potential. There are two plausible readings of the Commissioner’s reliance on section 280E. We address both.
> One plausible reading is that the revenue officer and the reviewing settlement officer rejected the offer-in-compromise because they thought section 280E required the disallowance of business expenses in a marijuana business when calculating the reasonable collection potential. But section 280E addresses deductions and credits, not the computation of reasonable collection potential. It is found in subtitle A, which relates to income tax, subchapter B, which relates to the computation of taxable income, and part IX, which identifies items that are not deductible. Of course, the location or grouping of Code sections is not to be given legal effect. See I.R.C. § 7806(b). But the text of section 261, the first Code section in part IX, makes clear that the provisions in that part relate to computing taxable income, providing: “In computing taxable income no deduction shall in any case be allowed in respect of the items specified in this part.” (Emphasis added.) And the text of section 280E makes clear that it applies to deductions and credits, providing: “No deduction or credit shall be allowed for any amount paid or incurred during the taxable year in carrying on any trade or business . . . of trafficking in controlled substances . . . .” (Emphasis added.) Simply stated, section 280E disallows deductions or credits for any amount paid or incurred in carrying on the trade or business of trafficking in controlled substances; it does not address what expenses may or may not be considered for the purpose of calculating a taxpayer’s reasonable collection potential. Accordingly, rejecting the offer-in-

**Source [165 T.C. No. 13, at *6]**

> issued two Notices of Determination sustaining the Notices of Intent to Levy. The two Notices of Determination provided the same explanation for rejecting Mission’s offer-in-compromise, concluding that “[t]he revenue officer did not allow all other operating expenses per Section 280e [sic] – you are involved in cannabis business, which is considered an illegal business activity for federal purposes.”
> Mission filed two Petitions challenging the Commissioner’s denial of the offer-in-compromise. Mission argues that the Commissioner abused his discretion by disallowing business expenses when calculating Mission’s reasonable collection potential. Mission argues that IRM 5.8.5.25.2 (Sept. 24, 2021), Calculation of Future Income – Cultivation and Sale of Marijuana in Accordance with State Laws, is in conflict with the Code, Treasury regulations, and other IRM provisions. The Commissioner argues that the settlement officer did not abuse her discretion in rejecting the proposed offer-in-compromise and sustaining the proposed collection action. The Commissioner argues that the policy to exclude expenses that are disallowed by section 280E when computing reasonable collection potential is consistent with the congressional intent underlying section 280E and is consistent with the discretion granted by Congress to set guidelines for offers-incompromise.
> Discussion
> I.
> Standard of Review

**Source [165 T.C. No. 13, at *43-44]**

> 6 2025 Allowable Living Expenses National Standards, IRS (Apr. 21, 2025), https://www.irs.gov/pub/irs-sbse/national-standards.pdf.
> Commissioner volunteered in his brief that this refusal is limited to his evaluation of one collection alternative: OICs. When a marijuana seller applies for an installment agreement—a form of settlement in which a tax liability is paid or partially paid over time—the Commissioner admitted that he considers nondeductible expenses, even those excluded under section 280E, in calculating his ability to pay. Respondent’s Answering Brief at 74. The Commissioner’s only argument for this incongruity is that installment agreements, unlike OICs, have safeguards to protect the agency in the form of biannual reviews to check if a taxpayer’s finances have changed. But I can’t see how this distinction makes a textual difference in deciding whether a taxpayer’s “available” income should include nondeductible expenses.
> I therefore dissent, because today we neither apply nor even mention this regulation—a regulation that echoes the Code and refers to collectability that is doubtful because of a taxpayer’s available, not taxable, income.
> B.
> There are problems with this approach. The most obvious is that none of the determinations that IRS Appeals made regarding tax years 2016–21 relied on public-policy grounds to reject Mission’s offers. Chenery tells us to rely on the reasoning used by the agency when it made its determination, not by the agency’s lawyers in defending it.7
> This should be enough to rule in Mission’s favor, but the Commissioner makes a number of other arguments, mostly on the basis of public policy.8 The Commissioner is correct that there is a public policy (at least at the federal level) against selling marijuana. He surmises that there is at least a small bud of an important distinction here—there is certainly no public policy against paying personal expenses, but there is against running a marijuana dispensary. He also

**Source [165 T.C. No. 13, at *2-3]**

> JENKINS and HOLMES, JJ., joined.
> JENKINS, J., wrote a dissenting opinion, which
> LANDY and HOLMES, JJ., joined.
> HOLMES, J., wrote a dissenting opinion, which
> LANDY, J., joined.
> —————
> Joseph A. Broyles, for petitioner.
> Nora Demirjian, S. Penina Shadrooz, and Yervant P. Hagopian, for respondent.
> OPINION
> BUCH, Judge: Mission Organic Center, Inc. (Mission), is a statelegal marijuana dispensary based in California that has unpaid income tax liabilities for 2016 through 2020 (years in issue).1 The Commissioner
> 1 Docket No. 9456-23L, involving Mission’s 2021 income tax liability, was previously consolidated with these cases. The Court has severed that case from these
> initiated collection actions, and Mission made an offer-in-compromise seeking to resolve its unpaid liabilities. The Commissioner evaluated the offer-in-compromise by calculating Mission’s reasonable collection potential and comparing it to the amount of Mission’s offer. In calculating Mission’s reasonable collection potential, the Commissioner did not take into account business expenses that are not deductible as a result of the application of section 280E.2 The Commissioner rejected Mission’s offer and issued Notices of Determination. Mission challenged the Commissioner’s determination to reject Mission’s offer claiming it was an abuse of discretion to disallow the business expenses that were necessary for the production of Mission’s income.
> The Commissioner has an established policy to disregard for reasonable collection potential purposes business expenses that are rendered nondeductible by section 280E. The policy is stated in the Commissioner’s Internal Revenue Manual (IRM) and is predicated on Congress’s enactment of section 280E. Creating this public policy exception is within the authority granted to the Commissioner under section 7122(d) to prescribe guidelines for accepting offers-incompromise. We resolve the issue in favor of the Commissioner.
> Background

**Your verdict:** yes

<details><summary>Verifier / reference</summary>verifier no (Sources cite congressional intent and discretion arguments, but Source 4 shows the Commissioner argues policy is consistent with these, not that the Court upheld it.); reference yes (Source 4 gives the Commissioner's argument on congressional intent and discretion, and Source 7 says the court resolved the issue for the Commissioner under section 7122(d).)</details>

---

## R26 `G-X25#0#0`

**Question:** My client's company pays its owner, who also works in the business, mostly through 'royalty' payments. The IRS says they are wages. Is section 530 relief available?

**Sentence:** The IRS classifies payments made to an owner-employee as wages rather than royalties if the payments are for services rendered in the business.

**Source [121 T.C. No. 6, at *25-26]**

> agreement between petitioner and Ms. Odell which provides for
> petitioner’s payment of royalties to Ms. Odell for its use of
> certain intangible property rights. We also understand that a
> royalty may be paid for the use of valuable intangible property
> rights. Or. State Univ. Alumni Association v. Commissioner,
> 193 F.3d 1098 (9th Cir. 1999), affg. T.C. Memo. 1996-34 and
> Alumni Association of Univ. of Or. Inc., v. Commissioner, T.C.
> Memo. 1996-63. We do not believe, however, that petitioner’s
> payments of any of the disputed amounts to Ms. Odell were
> royalties under the facts herein. Whereas Ms. Odell had used the
> referenced intangible property in her sole proprietorship to earn
> self-employment income subject to self-employment tax, we do not
> believe that she can avoid the payment of Federal employment
> taxes simply by declaring that she will be paying royalties to
> herself through a controlled corporation for its use of that
> property.
> We sustain respondent’s determination that petitioner paid
> all of the disputed amounts to Ms. Odell as wages.
> 4. Section 530 Relief
> Petitioner argues that it is entitled to relief under
> section 530 of the Revenue Act of 1978. When applicable, section
> 530 affords a taxpayer such as petitioner relief from employment
> taxes notwithstanding that the relationship between the taxpayer
> and the individual performing services would otherwise require
> the payment of those taxes. Section 530 provides in part:
> SEC. 530. CONTROVERSIES INVOLVING WHETHER INDIVIDUALS ARE EMPLOYEES FOR PURPOSES OF THE EMPLOYMENT TAXES.
> (a) Termination of Certain Employment Tax
> Liability * * *–-
> (1) In general.--If--
> (A) for purposes of employment taxes, the taxpayer
> did not treat an individual as an employee for any period * * *, and
> (B) in the case of periods after December 31,

**Your verdict:** no

<details><summary>Verifier / reference</summary>verifier yes (Source 1 states IRS determined payments were wages based on services rendered, not royalties.); reference no (Source 1 held these royalties were wages on its facts (prior self-employment use of property); it does not state a general rule about payments for services.)</details>

---

## R27 `G-C26#0#1`

**Question:** Settlement money was paid into my client's lawyer's trust account in December but held there because of a fee dispute. Is it income that year or when it is released?

**Sentence:** The IRS does not apply the doctrine of constructive receipt in this situation because the taxpayer did not delay the payment of the settlement amount.

**Source [T.C. Memo. 2006-239, at *19]**

> Gale v . Commissioner , T .C . Memo . 2002-54, funds from a lawsuit
> against United Ready Mixed were paid at the taxpayer's direction,
> under the terms of a settlement agreement signed by the taxpayer,
> to the taxpayer's attorney, to be deposited into an attorney-
> client trust account . The funds were placed into the trust
> account pending resolution of a dispute about attorney' s fees .
> However, the Court stated in Gale :
> There is no need to consider the doctrine of constructive receipt because petitioner did not delay United Ready Mixed's payment .'Z As between petitioner and United Ready Mixed, the settlement amount was fully paid in 1992 . United Ready Mixed retained no interest in the funds after they were paid, at petitioner's direction pursuant to the terms of the settlement agreement, to petitioner's attorney . Any restriction placed on the use of the settlement proceeds after payment by United Ready Mixed, whether the restriction was placed on the funds voluntarily by petitioner or through acts by petitioner's creditors, does not delay petitioner's receipt of the income for income tax purposes . [ Gale v . Commissioner , supra ; citations omitted . ]
> 12 "Constructive receipt" as defined in sec . 1 .451-2(a), Income Tax Regs ., is a legal term of art

**Your verdict:** no

<details><summary>Verifier / reference</summary>verifier yes (Source 1 explicitly states constructive receipt doctrine does not apply because taxpayer did not delay the settlement payment.); reference no (Source 1 says the court saw no need to consider constructive receipt; it does not say the IRS does not apply it.)</details>

---

## R28 `G-X26#0#3`

**Question:** My client is a retired teacher who writes and researches a book at home, reporting losses every year with almost no income. Can she deduct the expenses?

**Sentence:** Additionally, personal expenses cannot be deducted under the guise of business expenses, which may apply if the client is reporting losses with almost no income.

**Source [T.C. Memo. 2024-75, at *17-18]**

> Ms. Jones-Mazotti did not keep formal books and records related to her purported writer-researcher expenses. And she has never run a profit-and-loss statement. Moreover, the Mazottis claimed deductions for personal expenses such as family vacations, clothing, food, home improvements, and vehicle maintenance and repair costs. When pressed about the nature of the deductions, Ms. Jones-Mazotti was evasive and often unable to explain how these personal deductions related to her purported writer-researcher business activities. A reasonable and prudent person would know that personal expenses may not be deducted under the guise of business expenses.
> Under the circumstances, we conclude that the Mazottis were negligent in that they failed to make reasonable attempts to comply with the tax law and to determine the correctness of deductions that should have seemed too good to be true. See Neonatology Assocs., P.A. v. Commissioner, 299 F.3d at 234 (“When, as here, a taxpayer is presented with what would appear to be a fabulous opportunity to avoid tax obligations, he should recognize that he proceeds at his own peril.”).
> Further, “[o]nly one accuracy-related penalty may be applied with respect to any given portion of an underpayment, even if that portion is subject to the penalty on more than one of the grounds set forth in section 6662(b).” Sampson v. Commissioner, T.C. Memo. 2013-212, at *7–8 (citing New Phx. Sunrise Corp. & Subs. v. Commissioner, 132 T.C. 161, 187 (2009), aff’d, 408 F. App’x 908 (6th Cir. 2010)). Consequently, we need not determine whether the Mazottis are liable
> for penalties understatements of income tax for the 2018 and 2019 taxable years.
> for underpayments due
> substantial
> to
> V.
> Conclusion

**Source [T.C. Memo. 2024-75, at *3]**

> recall whether she spoke with those authors about minimizing expenses related to her writing.
> Ms. Jones-Mazotti has claimed business expense deductions related to her writer-researcher activities since approximately 1996 or 1997, and she identified 2022 as the first year in which she earned a profit related to those activities. Despite her tenure as a professed writer-researcher, she does not have a business plan for her writerresearcher activities.
> Ms. Jones-Mazotti claims that she has engaged in several different types of writer-researcher activities, including writing books, articles, and commercials, as well as travel for research and photography. We will discuss each in turn. We will also address Ms. Jones-Mazotti’s work with the Jefferson County School District.
> 1. Books
> When she began writing, Ms. Jones-Mazotti retained an agent to assist with her publishing journey. But after concluding that the agent was “less than ethical,” she decided to no longer work with the agent. She submitted several books to publishers in the early 1990s, but she received numerous rejection letters.
> Ms. Jones-Mazotti’s testimony about attempts to publish in the nearly 30 years since—including during the tax years at issue—was inconsistent. For example, she first testified that, during the tax years at issue, her time was mostly limited to writing “articles and storytelling and online,” not publishing efforts. She later testified that she submitted “every book” to potential publishers during the tax years at issue. But she could not recall any specific books that she queried to publishers and then stated it was “mostly articles” during the tax years at issue.
> Ms. Jones-Mazotti claims to have self-published approximately six books through Shutterfly. Her books include If You Grew Up In, Bountiful Journey, Can You Go Home Again, and Filthy Fingers. She also collaborated on a book with her daughter titled How to be a Bridesmaid.

**Your verdict:** yes

<details><summary>Verifier / reference</summary>verifier yes (Source 2 explicitly states personal expenses cannot be deducted under guise of business expenses.); reference no (Source 2 says personal expenses may not be deducted as business expenses, but nothing links this to the client's losses with almost no income.)</details>

---

## R29 `G-C13#0#6`

**Question:** Are a farmer's heavy-duty pickup trucks subject to the strict substantiation rules for listed property?

**Sentence:** The Court held that the strict substantiation requirements of section 274(d) do not apply to certain modified pickup trucks used exclusively for farming purposes.

**Source [T.C. Memo. 2022-117, at *33]**

> 
> The Court held supra that the strict substantiation requirements of section 274(d) are not applicable to the 1995 Ford F250, the 1999 Ford F350, which served as Mr. Hoakison’s tool truck, the 2008 Ford F350, or the 2011 Ford F350. Petitioners have demonstrated the business use and purpose of those vehicles, and the payments to State Farm and the Union County Treasurer with respect to those vehicles will be allowed as deductions. The strict substantiation requirements are applicable to the 1999 Dodge Dakota, however, and petitioners have not satisfied those requirements. They have not provided sufficient substantiation of the business use of the vehicle. Accordingly, those deductions will not be allowed. Similarly, petitioners have not introduced any information regarding the use of the 1992 Chevy S10, and respondent’s disallowance of a deduction for the insurance payment for that vehicle is also sustained.
> With respect to the payments to Farmers Mutual, petitioners introduced into evidence pages from a 2015 invoice showing $1,492 due and bank records showing payment of the invoice. The invoice lists several vehicles and other equipment covered by the policy, but petitioners have not introduced any additional evidence connecting those items with the farming operation or, in the case of the vehicles, have not satisfied the requirements of section 274(d). On the basis of the invoice and petitioners’ other records, the Court will allow an additional deduction of $36, representing the premiums paid for equipment designated on the invoice as “Farm Use Only.” The remaining amounts paid to EMC and Farmers Mutual are disallowed.

**Source [T.C. Memo. 2022-117, at *18]**

> Section 274(d)(4) provides that no deduction shall be allowed “with respect to any listed property (as defined in section 280F(d)(4))” unless the taxpayer substantiates “by adequate records or by sufficient evidence corroborating the taxpayer’s own statement.” Listed property includes, among other things, any passenger automobile or any other property used as a means of transportation. § 280F(d)(4)(A)(i) and (ii). The flush text of section 274(d), however, excludes from the strict substantiation requirements any “qualified nonpersonal use vehicle.” A “qualified nonpersonal use vehicle” is “any vehicle which, by reason of its nature, is not likely to be used more than a de minimis amount for personal purposes.” § 274(i). The strict substantiation requirements of section 274(d) generally apply to any pickup truck or van “unless the truck or van has been specially modified with the result that it is not likely to be used more than a de minimis amount for personal purposes.” Treas. Reg. § 1.274-5(k)(7). Other qualified nonpersonal use vehicles not subject to the strict substantiation requirements of section 274(d) include several relevant categories. Those include any vehicle designed to carry cargo with a loaded gross vehicle weight over 14,000 pounds, combines, flatbed trucks, and tractors and other special purpose farm vehicles. Treas. Reg. § 1.274-5(k)(2)(ii)(C), (F), (J), (Q). Respondent has previously conceded additional depreciation of $5,228 for each year with respect to a combine and an additional section 179 deduction of $9,800 with respect to a flatbed trailer for 2013.

**Source [T.C. Memo. 2022-117, at *18-19]**

> Respondent argues that the depreciation and other deductions claimed in connection with petitioners’ pickup trucks and other vehicles are subject to the strict substantiation requirements of section 274(d). Petitioners argue that section 274(d) is inapplicable to the pickup trucks because each was modified in some way to be used on the farm and was not likely to be used more than a de minimis amount for personal purposes. With respect to the 1995 Ford F250 and the 1999 Ford F350, the Court agrees. The 1995 Ford F250 had a bale stabber attached and was used exclusively to transport hay, and the 1999 Ford F350 was equipped with tools and equipment, including a torch, oil, and two 60gallon fuel tanks. The Court finds that both were modified with the result that they were not likely to be used more than a de minimis amount for personal purposes and that the strict substantiation requirements of section 274(d) do not apply with respect to those two trucks.
> The 2008 Ford F350 and the 2011 Ford F350 were both one-ton diesel engines that petitioners used to transport livestock between farms, to the veterinarian, or to market. Petitioners kept trailers
> attached to both trucks at nearly all times, including a 24-foot flatbed and a 30-foot livestock trailer for transporting livestock to the veterinarian in the case of an emergency. On the basis of petitioners’ credible testimony, as well as the weight and function of the vehicles and the attached trailers, the Court finds that strict substantiation requirements of section 274(d) do not apply with respect to the 2008 Ford F350 and the 2011 Ford F350.

**Your verdict:** yes

<details><summary>Verifier / reference</summary>verifier yes (Source 2 and 3 show Court held strict substantiation inapplicable to certain modified pickup trucks used for farming purposes.); reference no (Court held this for some trucks, but not all were modified or used exclusively for farming (e.g., F350s with trailers; only F250 exclusive).)</details>

---

## R30 `G-C24#0#3`

**Question:** Can a taxpayer deduct a home office for an activity the court has found is not engaged in for profit?

**Sentence:** The court has held that if a taxpayer does not conduct an activity with the requisite profit objective, then the expenses related to that activity are not deductible.

**Source [T.C. Memo. 2023-128, at *14]**

> III. Home Office Deductions
> Generally, the expenses of maintaining a household, including amounts paid for rent, water, utilities, and the like, are not deductible. Treas. Reg. § 1.262-1(b)(3). Section 280A(a) provides that “no deduction otherwise allowable under this chapter shall be allowed with respect to the use of a dwelling unit which is used by the taxpayer during the taxable year as a residence.” If, however, a portion of the residence is used as a place of business, a share of the expenses properly attributable to the portion of the property used for the business may be deductible as a business expense, subject to the rules of section 280A. § 280A(c).
> No deduction is allowed with respect to a home office unless “allocable to a portion of the dwelling unit which is exclusively used on a regular basis” as the taxpayer’s principal place of business. § 280A(a),
> 7 Respondent argues, in the alternative, that even if petitioner intended to earn a profit from Ovium, his expenses should be amortized as startup expenses. See §§ 195(a), (b), and (c)(1), 162(a); Jackson v. Commissioner, 86 T.C. 492, 514 (1986) (finding no deduction under section 162 unless related to an ongoing business), aff’d, 864 F.2d 1521 (10th Cir. 1989). We need not address this argument because, as explained above, we find that petitioner did not conduct the Ovium activity for profit; therefore, petitioner’s expenses are not eligible for amortization as section 195 startup expenses. See § 195(b)(1), (c)(1)(A) (providing amortization is allowed only for expenses that are incurred to create new trade or business); Commissioner v. Groetzinger, 480 U.S. at 35 (finding that a profit motive is required to have a trade or business); Wilmot v. Commissioner, T.C. Memo. 2011-293 (finding amortization under section 195 need not be addressed where activity is not conducted for a profit).

**Source [T.C. Memo. 2023-128, at *15]**

> Petitioner deducted $12,840 in rent expenses for his southern California apartment as “office” expenses under Schedule A miscellaneous itemized deductions for 2011 and 2012. At various points, petitioner has argued that the “office” expense was a Schedule C expense incurred in connection with Ovium,8 and at other points he has argued that it was a Schedule A expense incurred in connection with his employment at SRA OSS.9 We may consider each of these activities, because expenses attributable to the use of a home office may be deductible in conducting two or more separate business activities. Hamacher v. Commissioner, 94 T.C. 348, 356 (1990). However, if any activity conducted in the home office fails to meet the requirements of section 280A(c)(1), none of the activities meets the exclusive use requirement for the home office. Hamacher, 94 T.C. at 356.
> With respect to the Ovium activity, petitioner may deduct only an expense allocable to a portion of the apartment that is exclusively used on a regular basis as (1) the principal place of business for any trade or business of the taxpayer or (2) a place of business which is used by patients, clients, or customers in meeting or dealing with the taxpayer in the normal course of his or her trade or business. § 280A(c)(1)(A) and (B). We have held that the Ovium activity lacked a profit motive; it is therefore not a trade or business. See Commissioner v. Groetzinger, 480 U.S. at 35. As both factors under section 280A(c)(1) require the existence of a trade or business, we hold that petitioner’s use of the home

**Source [T.C. Memo. 2023-128, at *13-14]**

> Personal motives and recreational elements enjoyed in carrying on an activity may indicate that the activity is not engaged in for profit. Id. subpara. (9). Satisfaction from the work, rather than a profit motive, may account for a taxpayer’s persistence in certain loss-generating activities. See Foster, T.C. Memo. 2012-207. An activity is not classified as a hobby simply because the taxpayer finds it pleasurable. Jackson v. Commissioner, 59 T.C. 312, 317 (1972).
> Petitioner provided a substantial number of receipts for his Ovium activity for the years at issue. The receipts are for fast food and restaurants, coffee shops, bakeries, grocery stores, movie theaters, and hockey games. The receipts further reflect that petitioner made retail purchases at Walmart, Uniqlo, the North Face, REI, and BevMo!, and took a trip to Japan. Petitioner has failed to demonstrate a business
> purpose for these abundant expenditures for food, entertainment, and travel. By contrast, we searched in vain for any receipts for purchases of raw materials or equipment necessary for Ovium’s purported business activity. We conclude that a significant portion of the expenditures for the Ovium activity was personal. This factor favors respondent.
> J.
> Conclusion
> Considering all the facts and circumstances and weighing the factors analyzed above, we hold that petitioner did not conduct his Ovium activity in a businesslike manner and he did not engage in that activity with the requisite profit objective during the years at issue. We accordingly sustain respondent’s determination that petitioner is not entitled to deductions under section 183(b) for his reported Schedule C expenses for 2011 and 2012.7
> III. Home Office Deductions

**Your verdict:** no

<details><summary>Verifier / reference</summary>verifier yes (Source 3 states court held petitioner did not engage activity with requisite profit objective, therefore not entitled to deductions.); reference no (Source 3 sustains denial of only §183(b) deductions, and Source 2 denies home office; no general holding of non-deductibility.)</details>

---

## R31 `G-S23#0#0`

**Question:** A self-employed client wants to deduct groceries and household bills as business costs. Is that allowed?

**Sentence:** Generally, the expenses of maintaining a household, including amounts paid for groceries and household bills, are not deductible.

**Source [T.C. Memo. 2023-128, at *14]**

> III. Home Office Deductions
> Generally, the expenses of maintaining a household, including amounts paid for rent, water, utilities, and the like, are not deductible. Treas. Reg. § 1.262-1(b)(3). Section 280A(a) provides that “no deduction otherwise allowable under this chapter shall be allowed with respect to the use of a dwelling unit which is used by the taxpayer during the taxable year as a residence.” If, however, a portion of the residence is used as a place of business, a share of the expenses properly attributable to the portion of the property used for the business may be deductible as a business expense, subject to the rules of section 280A. § 280A(c).
> No deduction is allowed with respect to a home office unless “allocable to a portion of the dwelling unit which is exclusively used on a regular basis” as the taxpayer’s principal place of business. § 280A(a),
> 7 Respondent argues, in the alternative, that even if petitioner intended to earn a profit from Ovium, his expenses should be amortized as startup expenses. See §§ 195(a), (b), and (c)(1), 162(a); Jackson v. Commissioner, 86 T.C. 492, 514 (1986) (finding no deduction under section 162 unless related to an ongoing business), aff’d, 864 F.2d 1521 (10th Cir. 1989). We need not address this argument because, as explained above, we find that petitioner did not conduct the Ovium activity for profit; therefore, petitioner’s expenses are not eligible for amortization as section 195 startup expenses. See § 195(b)(1), (c)(1)(A) (providing amortization is allowed only for expenses that are incurred to create new trade or business); Commissioner v. Groetzinger, 480 U.S. at 35 (finding that a profit motive is required to have a trade or business); Wilmot v. Commissioner, T.C. Memo. 2011-293 (finding amortization under section 195 need not be addressed where activity is not conducted for a profit).

**Your verdict:** yes

<details><summary>Verifier / reference</summary>verifier yes (Source 1 explicitly states household expenses including utilities are not deductible; groceries fall within maintaining a household.); reference no (Source lists rent, water, utilities and the like; it does not mention groceries, though household bills roughly covered.)</details>

---

## R32 `G-C14#0#2`

**Question:** Will the Tax Court estimate a client's business expenses under the Cohan rule if the client kept records but didn't produce proof of payment?

**Sentence:** If the taxpayer has kept records but fails to produce proof of payment, the Court may still estimate the expenses, but it will bear heavily against the taxpayer due to the lack of substantiation.

**Source [T.C. Memo. 2013-215, at *22-23]**

> not meet the requirements of section 7491(a) for shifting the burden of proof
> to the IRS since, as discussed below, he failed to produce credible evidence,
> substantiate his deductions, and maintain adequate records. Thus, the burden
> remains on Mr. Phillips to establish that he is entitled to the deductions he claimed
> on his Schedule C as "other expenses". See Rule 142(a); New Colonial Ice Co. v.
> Section 162(a) allows a taxpayer to deduct all ordinary and necessary
> expenses paid or incurred by the taxpayer in carrying on a trade or business. An
> expense is "ordinary" if it is "normal, usual, or customary" in the taxpayer's trade
> or business. See Deputy v. du Pont, 308 U.S. 488, 495 (1940). An expense is
> "necessary" if it is "appropriate and helpful" in the taxpayer's business, but it need
> not be absolutely essential. Commissioner v. Tellier, 383 U.S. 687, 689 (1966)
> (citing Welch v. Helvering, 290 U.S. at 113). Whether an expense is deductible
> under section 162 is a question of fact to be decided by this Court on the basis of
> all the relevant facts and circumstances. Cloud v. Commissioner, 97 T.C. 613, 618
> Taxpayers are required to maintain records sufficient to establish the
> amounts of allowable deductions and to enable the IRS to determine the correct
> some types of expenses, lack of substantiation can be overcome. Under the
> Cohan doctrine, if a taxpayer establishes that a deductible expense has been paid
> but cannot establish the precise amount of the deductible expense, the Court may
> estimate the amount. See Cohan v. Commissioner, 39 F.2d 540, 543-544 (2d Cir.
> 1930)." In making the estimate, the Court bears heavily against the taxpayer who
> failed to more precisely substantiate the expense. See id. at 544. The Court will
> not estimate a deductible expense unless the taxpayer presents a sufficient

**Your verdict:** no

<details><summary>Verifier / reference</summary>verifier yes (Source 1 states Court may estimate when records kept but substantiation lacking, and bears heavily against taxpayer.); reference no (Source 1 covers estimating and bearing heavily against the taxpayer, but says nothing about taxpayers who kept records yet produced no proof of payment.)</details>

---

## R33 `G-C04#0#1`

**Question:** Can a medical practice get section 530 relief from employment taxes for physicians it treated as independent contractors, even if it filed its information returns late?

**Sentence:** The timely filing of information returns is a requirement for eligibility under section 530 relief.

**Source [120 T.C. No. 15, at *1-2]**

> 120 T.C. No. 15
> UNITED STATES TAX COURT
> MEDICAL EMERGENCY CARE ASSOCIATES, S.C., AN ILLINOIS CORPORATION, Petitioner v. COMMISSIONER OF INTERNAL REVENUE, Respondent
> Docket No. 8259-01. Filed May 19, 2003.
> P was a medical service corporation that provided emergency medical services to hospitals. P contracted with physicians to staff hospital emergency rooms. P treated those physicians as independent contractors. P failed to timely file required Forms 1096 and 1099, for 1996. P delinquently filed those forms on a basis consistent with its treatment of the physicians as independent contractors.
> R determined that the physicians were employees, and that P was not eligible for relief under sec. 530 of the Revenue Act of 1978, Pub. L. 95-600, 92 Stat. 2885, as amended (sec. 530). R determined that P did not meet the filing requirement of sec. 530(a)(1)(B). R’s interpretation of sec. 530(a)(1)(B) requires that a taxpayer timely file all required returns in order to be eligible for sec. 530 relief.
> This Court granted R’s motion to sever and continue determinations of worker classification and proper employment taxes until after our consideration of P’s eligibility for relief under sec. 530.
> Held: Because P did not treat the physicians as
> employees for any period, filed all Federal tax returns on a basis consistent with P’s treatment of the physicians as not being employees, and had a reasonable basis for not treating the physicians as employees, P is entitled to relief from employment tax liability pursuant to sec. 530. P’s untimely filing of information returns does not preclude P from qualifying for such relief, particularly in the circumstances of this case.
> Carmen J. Mitchell, for petitioner.
> Linda C. Grobe and David S. Weiner, for respondent.
> NIMS, Judge: The petition in this case was filed in
> response to a Notice of Determination Concerning Worker
> Classification Under Section 7436 (notice of determination)

**Source [120 T.C. No. 15, at *13-14]**

> THE COURT: Suppose a taxpayer is required to file
> the 1096 and the 1099s and the office burns down two weeks before the due date and the taxpayer writes a letter to the--well, I don’t know who, but somebody in the IRS and says, Look, our office burned down and our records are destroyed; we need some additional time. You’re not saying that the statute would preclude the Government from granting an extension of time, are you?
> MS. GROBE: Yes, Your Honor. I am.
> *
> *
> *
> *
> *
> *
> *
> This is a relief section. They still have the ability to come in and argue that these workers are not independent contractors--rather, are not employees; they are independent contractors.
> The “relief” proposed by respondent’s counsel presents
> precisely the situation that section 530 was enacted to avoid.
> In the case before us respondent has proposed a deficiency in the
> amount of $256,628.61, to dispute which, under respondent’s
> theory, petitioner would be required to prove the status of each
> of the reclassified physicians. The tax liability of each of the
> reclassified physicians would likewise be affected.
> We repeat that respondent correctly states that timely
> filing of returns is required throughout the Internal Revenue
> Code. This includes Forms 1096 and 1099. The consequences of
> “Failure to Comply with Certain Information Reporting
> Requirements” are contained in sections 6721 through 6724.
> Section 6721(a) deals with “Failure to file correct information
> returns”, which includes Forms 1096 and 1099 (see section 6041A),
> and section 6721(a)(2)(A) describes a failure to file subject to
> penalty as “any failure to file an information return with the
> Secretary on or before the required filing date.” Section
> 6721(e) prescribes a “Penalty in case of intentional disregard”.
> Section 6722 provides for similar penalties in the case of
> “Failure to furnish correct payee statements”; section 6723

**Your verdict:** no

<details><summary>Verifier / reference</summary>verifier yes (Source 1 states timely filing is a requirement under section 530(a)(1)(B); Source 4 affirms timely filing of returns is required.); reference no (Sources reject IRS's view that timely filing is required for section 530 eligibility; Source 4 only says timely filing is required generally.)</details>

---

## R34 `G-C25#0#3`

**Question:** Has the Tax Court found spa workers who pay booth rent to be independent contractors rather than employees?

**Sentence:** The arrangement where the spa charged a fixed booth rent or a percentage of gross revenues was considered a factor supporting independent contractor status.

**Source [T.C. Memo. 2010-239, at *14-16]**

> in the beauty parlor for rent of 40 percent of their proceeds,
> with minimum rent of $50 per week). Respondent acknowledges that the spa's payout arrangement is "something of a hybrid" since it includes both a percentage split of gross revenues and a "minimum rent component". But respondent contends that this "minimum rent component" demonstrates "more control over the workers rather than less." If, however, as the
> Commissioner's revenue rulings suggest, a fixed rent arrangement
> evidences self-employment status'(since employees do not normally
> pay their employers rent for their workspace), we have difficulty
> understanding how a fixed rent component
> in a percentage payout
> formula weakens,
> rather than strengthens,
> the case for self-
> employment status. Although the spa was not wholly consistent
> in
> its policies,
> it appears that
> the spa generally did charge, and
> the service providers did generally pay, weekly rent of at least
> $80. We take this circumstance into account as one factor
> weighing against an employer-employee relationship.
> The weekly payment arrangement also reflected,
> in.addition
> to the spa's retention of rent, compensation of
> the service
> providers on a straight commission basis, with no minimum
> guaranteed level of payment.' This circumstance also counts in
> favor of
> independent contractor status, see Rev. Rul. 87-41,
> 1987-1 C.B. at 299, as does the fact 'that
> the spa provided the
> service providers no employee benefits, such as vacation or sick
> Respondent concedes that the spa did not pay service
> providers' business or travel expenses and thaE this circumstance
> supports independent contractor status.
> In addition,
> it appears
> that many of
> the massage therapists made significant investments
> in outfitting and decorating their massage rooms."
> These various
> circumstances, coupled with the spa's right to collect minimum
> fixed rent each week, also lead us to conclude that service
> providers bore the risk of suffering net
> losées, and in some
> Conversely,

**Source [T.C. Memo. 2010-239, at *1-3]**

> Massage therapists, cosmetologists, and nail
> technicians (service providers) operated on the premises of Ps' spa. provider weekly "booth rent" equal approximately $80 base rent or 25 percent of service provider's gross revenues. they had a landlord/tenant relationship with the service providers. providers were Ps' employees. Held: providers were independent contractors.
> Ps gederally charged each service
> to the greater of
> the
> Ps contend that
> R determined that the service The service
> Edith F. Moates,
> for petitioners.
> Denise G. Dengler,
> for respondent.
> THORNTON, Judge: Petitioners have brought
> these actions for
> redetermination of employment status pursuant
> to section 7436.1
> In a notice of determination of worker classification dated
> February 15, 2007,
> respondent determined that for 2002 petitioner
> Cheryl A. Mayfield Therapy Center
> (the therapy center) owed
> employment
> taxes of $20,473 and additions to tax under sections
> 6651 and 6656 of $4,607 and $1,211,
> respectively.
> In a separate
> notice of determination of worker classification dated
> petitioner Ardmore Day Spa,
> Inc.
> (the corporation), owed
> employment
> taxes, additions to tax, and penalties as follows:
> The issue is whether respondent properly classified certain
> massage therapists and cosmetologists as petitioners' employees.
> The parties have stipulated some facts, which we incorporate
> herein by this reference. When they filed their petitions,
> IUnless otherwise indicated, section references are to the
> Internal Revenue Code in effect for the years at references are to the Tax Court Rules of Practice and.Procedure. All
> issue. Rule
> figures are rounded to the nearest dollar.
> Cheryl A. Mayfield (Ms. Mayfield) , who is the sole proprietor of
> the therapy center,
> resided in Oklahoma, and the corporation had
> its principal place of business in Oklahoma.
> Ms. Mayfield is a licensed massage therapist. During 2002
> she operated the therapy center and a massage school at separate
> locations in Ardmore, Oklahoma. At
> the beginning of 2003 she
> combined these business activities in the corporation, of wh.ic

**Source [T.C. Memo. 2010-239, at *12-14]**

> the spa.retained as booth rent
> the greater of $80
> or 25 percent of
> the service provider's gross revenues. Although
> the spa wrote each service provider a weekly check for the
> balance of
> the customer fees that it collected, petitioners seem
> to suggest
> that
> they did so merely as financial
> intermediaries
> for the service providers.
> We find these contentions unpersuasive. Clients paid the
> spa, not
> the service providers.
> These funds were within the
> control and disposition of
> the spa until it paid the service
> providers by writing them checks.7
> See sec. 1.6041-1(h),
> Income
> Tax Regs.
> (a "payment"
> is made for purposes of section 6041
> information returns when an.amount
> is made available to a person
> "so that it may be drawn.at any time, and its receipt brought
> within his own control and disposition.."). Consequently, we
> conclude that
> the spa's week-ly checks to the service providers in
> fact~ represented payments to them. But this does not answer the
> question whether the payments were made to the service providers
> in their capacities as employees or as independent contractors.
> Some revenue rulings, concluding that certain beauticians
> and barbers are self-employed,
> take into account as part of
> the
> analysis the existence of a fixed-fee lease agreement.
> See Rev.
> 1957-1 C.B. 329 (barbers). Conversely, other revenue rulings,
> concluding that certain beauticians and similar professionals are
> Our conclusion in this regard is not altered by the fact that the service providers would sometimes take cash from the cash basket and leave notes. This practice seems to indicate less that the cash was in the service providers' dominion and control policy for making cash advances.
> than that the spa had a very lenient
> (and trusting)
> a percentage of gross receipts.
> See Rev. Rul. 73-591, 1973-2
> in the beauty parlor for rent of 40 percent of their proceeds,

**Source [T.C. Memo. 2010-239, at *18-19]**

> with the spa at any time. But we are not persuaded that this
> consideration adds much to our analysis, particularly given the
> informal nature of
> the relationship between the spa and its
> service providers.
> It may, however, help explain what appears to
> have been a significant level of
> turnover among the service
> providers, many of whom operated at
> the spa for only a short
> time.
> That consideration,
> in turn,
> leads us to think that
> although some other service providers operated at
> the spa for
> several years,
> the work relationship was not necessarily
> permanent or indefinite, as indicative of employment status.
> See
> Ewens & Miller,
> Inc. v. Commissioner, supra at 273.
> Consequently, we also regard this factor as neutral.
> Although this is a close case, weighing all
> the evidence we
> conclude that
> factors indicating the service providers' autonomy
> predominate over factors indicating petitioners' control over
> them. Accordingly, we conclude and hold that the service
> providers were independent contractors rather than petitioners'
> employees during the years at
> issue.
> To reflect the foregoing and petitioners' concessions,
> Decisions will be entered
> under Rule 155.

**Source [T.C. Memo. 2010-239, at *17-18]**

> whether they wished to participate.
> And although the spa
> assigned walk-in clients on a-rotating basis,
> the'service
> - providers retained the right to refuse any client.
> Arrayed against
> these considerations supporting independent
> contractor status are a number of
> factors supporting employee
> status for the service providers.
> In particular,
> their services
> were integrated into the spa's operations;
> they provided their
> services mostly, if not entirely, on the: spa's premises;
> the spa
> "Although many of
> the massage therapists initially trained they paid regular tuition for
> at Ms. Mayfield's massage school, these classes and had no guarantee of subsequently securing a spot at
> the spa.
> provided at
> least some informal training to new service
> providers;
> there is no showing that the service providers made
> their services available to the general public (other.than by
> working at
> the spa) regularly and consistently;
> they were
> assisted in booking appointments and in receiving payments by
> receptionists that the spa employed and supervised; clients paid
> the spa rather than the service providers; and the spa retained
> the payments until it distributed the service providers' weekly
> Otherfactors we consider neutral or ofe limited usefulness
> to our analysis.
> For instance, although there was no requirement
> that the service providers work full time for the spa, and
> although some of
> them in fact worked part time and had jobs
> elsewhere,
> these circumstances appear consistent with either
> independent contractor or part-time employee status.
> Likewise we
> regard as neutral
> the fact
> that
> the service providers rendered
> their services personally--a circumstance probably dictated by
> the nature of
> the services and the licensinè requirements.
> Respondent asserts as a factor evidencing an
> employer/employee relationship that petitioners had the right to
> terminate the services of any service provider at any time and
> that any service provider could terminate his or her relationship
> with the spa at any time. But we are not persuaded that this

**Source [T.C. Memo. 2010-239, at *11-12]**

> putative employer;
> (3) integration of
> the worker's services into
> business operations;
> (4) a requirement that the worker's services
> be rendered personally;
> (5) the putative employer's hiring,
> supervising, and paying assistants;
> (6) a continuing ·
> relationship;
> (7) set hours of work;
> (8) a requirement that the
> worker devote substantially full time for the putative employer
> rather than being free to work when and for whom he or she
> chooses;
> (9) doing work on the putative employer's premises;
> (10) requiring the worker to perform services in the order or sequence
> set by the putative employer;
> (11) requiring the worker to submit
> oral or written reports;
> (12) paying by the hour, week, or month,
> rather than by the job or on a straight commission;
> (13) paying
> business and travel expenses;
> (14) furnishing tools and
> - materials;
> (15) a lack of significant investment by the worker;
> (16) an absence of ability by the worker to realize a profit or
> suffer a loss;
> (17) working for no more thanione firm at a time;
> (18) the worker's not making his or her services available to the
> general public on a regular and consistent basis;
> (19) a right to
> discharge the worker; and (20) a right by the worker-to terminate
> the relationship without
> incurring liability. Rev. Rul. 87-41,
> Circuit,
> to which any-appeal of this case would lie, has endorsed
> applying these 20 factors.
> E.
> Inv. Corp. v. United States, 49
> observed, however, not every factor applies in every situation,
> and no one factor in isolation is dispositive; rather "'it is the
> total situation that controls.'"
> Id. at 653. (quoting Bartels v.
> .Petitioners contend that their relationship to the service
> providers was not that of an employer to employees but that of a
> landlord to tenants.
> They point to the fact that each week, as a
> general rule,
> the spa.retained as booth rent

**Source [T.C. Memo. 2010-239, at *16-17]**

> Conversely,
> the service providers had opportunities to profit by
> working longer hours, at
> times coming into the spa for
> appointments outside the spa's normal business hours. Finally,
> on the basis of
> the -testimony of several serùice sproviders,
> it
> relationship with the.spa." All
> these considerations support a
> finding of
> independent contractor status.
> See Ewens & Miller,
> Other factors also point to independenticontractor status.
> Respondent concedes that
> the spa did not tel
> the service
> providers how to provide their services to the clients.
> In fact,
> it appears -that
> the spa required the service providers to comply
> with only a relatively small number of
> instructions relating to
> the spa's operation.
> The service providers were all
> licensed
> "Although the record does not similarlys establish that the
> cosmetologists made significant investments, we assign this consideration little weight appear that a cosmetologist would ordinarilý require large expenditures to conduct that profession.
> in our analysis,since it would not
> "For instance, one of
> the massage therapists testified that
> in 2004, while operating at therapy business.
> the spa, she indorporated her massage
> professionals, possessing skills as required by their licensing."
> They set their own hours. Although they provided the spa with
> their schedules in advance,
> they changed those schedules asthey
> pleased:
> And although the spa posted operating hours and
> attempted to have coverage for all those hours,
> the service
> providers were not required to work those houts, and the spa
> sometimes closed early if no service provider wás available to
> work. Moreover,
> the service providers might work in the spa
> outside the posted hours, gaining access to the spa with their
> own keys. Although the spa posted prices for various services,
> the service providers were free to charge less and sometimes
> provided services for free. Similarly, although the spa promoted
> various "specials",
> the service providers were free to decide ~
> whether they wished to participate.

**Your verdict:** yes

<details><summary>Verifier / reference</summary>verifier yes (Source 2 discusses fixed rent and percentage arrangements as factors supporting independent contractor status.); reference no (Source 2 says fixed minimum rent weighed against employment; it does not treat a bare percentage of gross revenues as supporting independent status.)</details>

---

## R35 `G-C08#0#1`

**Question:** If a self-directed IRA buys American Eagle coins and the owner keeps them at home, is that a distribution?

**Sentence:** The term 'collectible' includes any coin, such as American Eagle coins.

**Source [26 U.S.C. § 408(m)-(n)]**

> (m) Investment in collectibles treated as distributions. (1) In general. The acquisition by an individual retirement account or by an individually-directed account under a plan described in section 401(a) of any collectible shall be treated (for purposes of this section and section 402) as a distribution from such account in an amount equal to the cost to such account of such collectible.
> (2) Collectible defined. For purposes of this subsection, the term “collectible” means— (A) any work of art,
> (B) any rug or antique,
> (C) any metal or gem,
> (D) any stamp or coin,
> (E) any alcoholic beverage, or
> (F) any other tangible personal property specified by the Secretary for purposes of this subsection.
> (3) Exception for certain coins and bullion. For purposes of this subsection, the term “collectible” shall not include— (A) any coin which is— (i) a gold coin described in paragraph (7), (8), (9), or (10) of section 5112(a) of title 31, United States Code,
> (ii) a silver coin described in section 5112(e) of title 31, United States Code,
> (iii) a platinum coin described in section 5112(k) of title 31, United States Code, or
> (iv) a coin issued under the laws of any State, or
> (B) any gold, silver, platinum, or palladium bullion of a fineness equal to or exceeding the minimum fineness that a contract market (as described in section 5 of the Commodity Exchange Act, 7 U.S.C. 7) requires for metals which may be delivered in satisfaction of a regulated futures contract,
> if such bullion is in the physical possession of a trustee described under subsection (a) of this section.11 So in original. Concluding provisions probably should be part of subpar. (B).
> (n) Bank. For purposes of subsection (a)(2), the term “bank” means— (1) any bank (as defined in section 581),
> (2) an insured credit union (within the meaning of paragraph (6) or (7) of section 101 of the Federal Credit Union Act), and
> (3) a corporation which, under the laws of the State of its incorporation, is subject to supervision and examination by the Commissioner of Banking or other officer of such State in charge of the administration of the banking laws of such State.

**Your verdict:** no

<details><summary>Verifier / reference</summary>verifier yes (Source 1 section 408(m)(2)(D) lists 'any stamp or coin' as a collectible.); reference no (Source 1 defines collectible to include any coin but expressly excepts certain coins (gold/silver/platinum American Eagles); the claim omits this and wrongly implies AE coins are collectibles.)</details>

---

## R36 `G-S01#0#1`

**Question:** A client's horse breeding and showing operation has made a profit in 2 of the last 7 years. Is it presumed to be engaged in for profit?

**Sentence:** Since the client's horse breeding and showing operation has made a profit in 2 of the last 7 years, it meets the criteria for the presumption of being engaged in for profit.

**Source [26 CFR 1.183-1(c)(1)]**

> (c) Presumption that activity is engaged in for profit —(1) In general. If for:
> (i) Any 2 of 7 consecutive taxable years, in the case of an activity which consists in major part of the breeding, training, showing, or racing of horses, or
> (ii) Any 2 of 5 consecutive taxable years, in the case of any other activity, the gross income derived from an activity exceeds the deductions attributable to such activity which would be allowed or allowable if the activity were engaged in for profit, such activity is presumed, unless the Commissioner establishes to the contrary, to be engaged in for profit. For purposes of this determination the deduction permitted by section 1202 shall not be taken into account. Such presumption applies with respect to the second profit year and all years subsequent to the second profit year within the 5- or 7-year period beginning with the first profit year. This presumption arises only if the activity is substantially the same activity for each of the relevant taxable years, including the taxable year in question. If the taxpayer does not meet the requirements of section 183(d) and this paragraph, no inference that the activity is not engaged in for profit shall arise by reason of the provisions of section 183. For purposes of this paragraph, a net operating loss deduction is not taken into account as a deduction. For purposes of this subparagraph a short taxable year constitutes a taxable year.

**Your verdict:** yes

<details><summary>Verifier / reference</summary>verifier yes (Client meets the 2-of-7-years profit criterion stated in Source 1 for horse activities.); reference no (The source requires consecutive years and substantially the same activity; the facts don't say the 7 years were consecutive or the activity unchanged. Deductions are also measured as if the activity were for profit.)</details>

---

## R37 `G-S17#0#2`

**Question:** six year assessment period omission of more than 25 percent of gross income

**Sentence:** An amount omitted from gross income is not considered omitted if it is disclosed in the return or in a statement attached to the return in a manner adequate to apprise the Secretary of its nature and amount.

**Source [26 U.S.C. § 6501(e)(1)]**

> (e) Substantial omission of items. Except as otherwise provided in subsection (c)— (1) Income taxes. In the case of any tax imposed by subtitle A— (A) General rule. If the taxpayer omits from gross income an amount properly includible therein and— (i) such amount is in excess of 25 percent of the amount of gross income stated in the return, or
> (ii) such amount— (I) is attributable to one or more assets with respect to which information is required to be reported under section 6038D (or would be so required if such section were applied without regard to the dollar threshold specified in subsection (a) thereof and without regard to any exceptions provided pursuant to subsection (h)(1) thereof), and
> (II) is in excess of $5,000,
> the tax may be assessed, or a proceeding in court for collection of such tax may be begun without assessment, at any time within 6 years after the return was filed.
> (B) Determination of gross income. For purposes of subparagraph (A)— (i) In the case of a trade or business, the term “gross income” means the total of the amounts received or accrued from the sale of goods or services (if such amounts are required to be shown on the return) prior to diminution by the cost of such sales or services;
> (ii) An understatement of gross income by reason of an overstatement of unrecovered cost or other basis is an omission from gross income; and
> (iii) In determining the amount omitted from gross income (other than in the case of an overstatement of unrecovered cost or other basis), there shall not be taken into account any amount which is omitted from gross income stated in the return if such amount is disclosed in the return, or in a statement attached to the return, in a manner adequate to apprise the Secretary of the nature and amount of such item.
> (C) Constructive dividends. If the taxpayer omits from gross income an amount properly includible therein under section 951(a), the tax may be assessed, or a proceeding in court for the collection of such tax may be done without assessing, at any time within 6 years after the return was filed.

**Your verdict:** no

<details><summary>Verifier / reference</summary>verifier yes (Source 1 § 6501(e)(1)(B)(iii) states disclosed amounts are not counted as omitted if disclosed adequately.); reference no (Source (B)(iii) excludes basis-overstatement cases from the adequate disclosure rule; the claim states it without that exception.)</details>

---

## R38 `G-X06#0#1`

**Question:** My client is a real estate agent who incorporated. She is the only officer and the only person working for the corporation, and takes no salary. Is she its employee for employment tax purposes?

**Sentence:** However, an officer who does not perform any services or performs only minor services and does not receive any remuneration is not considered an employee of the corporation under 26 U.S.C. § 3121(d).

**Source [119 T.C. No. 5, at *7-8]**

> He
> reported income from petitioner in the amounts shown on the
> Schedules K-1;
> i.e., $33,196 and $24,990,
> for 1995 and 1996,
> respectively.
> For 1995, on Schedule C, Profit or Loss From
> Business (Schedule C), he reported $6,000 classified as
> "Management and Storage Rental of Office Space for Corporation,
> and Management and Accounting Services:
> 1099-MISC received".
> For 1996, on Schedule C, he reported $7,200, without any
> identification; on Form 4831, Rental
> Income, he reported $6,000
> as rental
> income attributable to his personal residence.
> Discussion
> I. Statutory and Regulatory Background
> A.
> Internal Revenue Code and Employment Tax Regulations
> Sections 3111 and 3301 impose employment
> taxes upon
> employers under FICA and FUTA,
> respectively, based on wages paid
> to employees. Section 3121(d) defines the term "employee"
> for
> purposes of the FICA tax. With certain modifications not
> relevant here,
> this definition applies for purposes of the FUTA
> tax as well.
> Sec. 3306(i).
> Under section 3121(d)(2),
> the term "employee"
> includes any
> individual who has the status of an employee under the common
> law. Paragraphs (1),
> (3), and (4) of section 3121(d) describe
> other individuals who are considered employees regardless of
> their status under the common law.
> Individuals described in
> those paragraphs are commonly referred to as "statutory"
> employees.
> One such category of statutory employees consists of
> officers of corporations.
> Sec. 3121(d)(1). Section 31.3121(d)-
> 1(b), Employment Tax Regs.,
> limits that category as follows:
> (b) Corporate officers.--Generally, an officer of
> the corporation.
> a corporation is an employee of However, an officer of a corporation who as such does not perform any services or performs only minor services and who neither receives nor is entitled to receive, directly or indirectly, any remuneration is the corporation. considered not *
> to be an employee of
> Section 31.3306(i)-1(e), Employment Tax Regs., contains a like
> limitation specifically applicable to the FUTA tax.
> B. Section 530 of the Revenue Act of 1978

**Your verdict:** yes

<details><summary>Verifier / reference</summary>verifier yes (Source 2 explicitly states officers performing only minor services and receiving no remuneration are not considered employees.); reference no (The limitation comes from Treas. Reg. 31.3121(d)-1(b), not the statute itself, and the regulation also says 'neither receives nor is entitled to receive' remuneration, which the claim omits. Attributing it to §3121(d) is inaccurate.)</details>

---

## R39 `G-X03#0#1`

**Question:** My client qualifies as a real estate professional and owns six rental houses. He never elected to treat them as one activity, and he is heavily involved in only two. Are all six rental losses nonpassive?

**Sentence:** Since the client qualifies as a real estate professional, the rental activities are not considered passive activities under section 469(c)(7).

**Source [26 U.S.C. § 469(c)(7)]**

> (7) Special rules for taxpayers in real property business. (A) In general. If this paragraph applies to any taxpayer for a taxable year— (i) paragraph (2) shall not apply to any rental real estate activity of such taxpayer for such taxable year, and
> (ii) this section shall be applied as if each interest of the taxpayer in rental real estate were a separate activity.
> Notwithstanding clause (ii), a taxpayer may elect to treat all interests in rental real estate as one activity. Nothing in the preceding provisions of this subparagraph shall be construed as affecting the determination of whether the taxpayer materially participates with respect to any interest in a limited partnership as a limited partner.
> (B) Taxpayers to whom paragraph applies. This paragraph shall apply to a taxpayer for a taxable year if— (i) more than one-half of the personal services performed in trades or businesses by the taxpayer during such taxable year are performed in real property trades or businesses in which the taxpayer materially participates, and
> (ii) such taxpayer performs more than 750 hours of services during the taxable year in real property trades or businesses in which the taxpayer materially participates.
> In the case of a joint return, the requirements of the preceding sentence are satisfied if and only if either spouse separately satisfies such requirements. For purposes of the preceding sentence, activities in which a spouse materially participates shall be determined under subsection (h).
> (C) Real property trade or business. For purposes of this paragraph, the term “real property trade or business” means any real property development, redevelopment, construction, reconstruction, acquisition, conversion, rental, operation, management, leasing, or brokerage trade or business.
> (D) Special rules for subparagraph (B). (i) Closely held C corporations. In the case of a closely held C corporation, the requirements of subparagraph (B) shall be treated as met for any taxable year if more than 50 percent of the gross receipts of such corporation for such taxable year are derived from real property trades or businesses in which the corporation materially participates.

**Your verdict:** no

<details><summary>Verifier / reference</summary>verifier yes (Source 2 § 469(c)(7)(A)(i) states paragraph (2) shall not apply to rental real estate activities of real estate professionals, exempting them from passive activity rules.); reference no (Source 2 says paragraph (2) doesn't apply to rental activities, but material participation in each activity is still needed; the claim overstates this.)</details>

---

## R40 `G-C24#0#0`

**Question:** Can a taxpayer deduct a home office for an activity the court has found is not engaged in for profit?

**Sentence:** No deduction is allowed for an activity that is not engaged in for profit under section 183.

**Source [26 U.S.C. § 183(a)-(d)]**

> (a) General rule. In the case of an activity engaged in by an individual or an S corporation, if such activity is not engaged in for profit, no deduction attributable to such activity shall be allowed under this chapter except as provided in this section.
> (b) Deductions allowable. In the case of an activity not engaged in for profit to which subsection (a) applies, there shall be allowed— (1) the deductions which would be allowable under this chapter for the taxable year without regard to whether or not such activity is engaged in for profit, and
> (2) a deduction equal to the amount of the deductions which would be allowable under this chapter for the taxable year only if such activity were engaged in for profit, but only to the extent that the gross income derived from such activity for the taxable year exceeds the deductions allowable by reason of paragraph (1).
> (c) Activity not engaged in for profit defined. For purposes of this section, the term “activity not engaged in for profit” means any activity other than one with respect to which deductions are allowable for the taxable year under section 162 or under paragraph (1) or (2) of section 212.
> (d) Presumption. If the gross income derived from an activity for 3 or more of the taxable years in the period of 5 consecutive taxable years which ends with the taxable year exceeds the deductions attributable to such activity (determined without regard to whether or not such activity is engaged in for profit), then, unless the Secretary establishes to the contrary, such activity shall be presumed for purposes of this chapter for such taxable year to be an activity engaged in for profit. In the case of an activity which consists in major part of the breeding, training, showing, or racing of horses, the preceding sentence shall be applied by substituting “2” for “3” and “7” for “5”.

**Your verdict:** no

<details><summary>Verifier / reference</summary>verifier yes (Source 1 section 183(a) states no deduction allowed for activity not engaged in profit.); reference no (Source 1 §183(a) bars deductions but §183(b) allows some deductions; the unqualified claim omits this exception.)</details>

---
