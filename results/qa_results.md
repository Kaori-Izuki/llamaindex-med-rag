# Homework 6 本地 RAG 问答结果

> 本文件由真实运行的 LlamaIndex 查询流程生成；每个问题都保留了 source_nodes、相似度分数和检索片段。

## 1. 事实型：根据这些文献，PD-1/PD-L1 与 CTLA-4 分别在 T 细胞激活的哪个阶段发挥抑制作用？它们解除抑制后主要带来哪些免疫学变化？

**回答**：

根据这些文章，PD-L1 在 T 组织细胞活化（T-cell activation）的早期阶段起着抑制作用，而 CTLA -4 则在 T 淋巴细胞活化的晚期阶段起作用，并通过其负调节作用来解除这种抑制。

- 运行时间：11.631 秒
- source_nodes 数量：3
- 参数：chunk_size=512，chunk_overlap=50，similarity_top_k=3，temperature=0.1

### source_nodes

#### Node 1
- 来源文件：`Wei_2017_Distinct_cellular_mechanisms_CTLA4_PD1.pdf.pdf`
- 相似度分数：`0.857513`
- 页码元数据：`13`
- 文本片段：Genomic and Transcriptomic Features of Response to Anti-PD-1  Therapy in Metastatic Melanoma. Cell. 2016; 165:35–44. [PubMed: 26997480]  Im SJ, Hashimoto M, Gerner MY , Lee J, Kissick HT, Burger MC, Shan Q, Hale JS, Lee J, Nasti TH, et  al. Defining CD8+ T cells that provide the proliferative burst after PD-1 therapy. Nature. 2016;  537:417–421. [PubMed: 27501248]  Kamphorst AO, Pillai RN, Yang S, Nasti TH, Akondy RS, Wieland A, Sica GL, Yu K, Koenig L, Patel  NT, et al. Proliferation of PD-1+ CD8 T cells in peripheral blood after PD-1-targeted therapy in  lung cancer patients. Proc Natl Acad Sci USA. 2017; 114:4993–4998. [PubMed: 28446615]  Koboldt DC, Zhang Q, Larson DE, Shen D, McLellan MD, Lin L, Miller CA, Mardis ER, Ding L,  Wilson RK. VarScan 2: somatic mutation and copy number alteration discovery in cancer by  exome sequencing. Genome Res.

#### Node 2
- 来源文件：`Cheng_2024_Dual_blockade_PD1_PDL1_CTLA4_lung_cancer.pdf`
- 相似度分数：`0.851812`
- 页码元数据：`24`
- 文本片段：171. Keir ME, Liang SC, Guleria I, Latchman YE, Qipo A, Albacker LA, et al.  Tissue expression of PD-L1 mediates peripheral T cell tolerance. J Exp  Med. 2006;203:883–95.  172. Tivol EA, Borriello F, Schweitzer AN, Lynch WP , Bluestone JA, Sharpe AH.  Loss of CTLA-4 leads to massive lymphoproliferation and fatal multiorgan tissue destruction, revealing a critical negative regulatory role of  CTLA-4. Immunity. 1995;3:541–7.  173. Freeman GJ, Long AJ, Iwai Y, Bourque K, Chernova T, Nishimura H, et al.  Engagement of the PD-1 immunoinhibitory receptor by a novel B7  family member leads to negative regulation of lymphocyte activation. J  Exp Med. 2000;192:1027–34. Publisher’s Note Springer Nature remains neutral with regard to jurisdictional claims in published maps and institutional affiliations.

#### Node 3
- 来源文件：`Cheng_2024_Dual_blockade_PD1_PDL1_CTLA4_lung_cancer.pdf`
- 相似度分数：`0.849928`
- 页码元数据：`21`
- 文本片段：2006;116:1935–45.  42. Simpson TR, Li F, Montalvo-Ortiz W, Sepulveda MA, Bergerhoff K, Arce  F, et al. Fc-dependent depletion of tumor-infiltrating regulatory T cells  co-defines the efficacy of anti-CTLA-4 therapy against melanoma. J Exp  Med. 2013;210:1695–710.  43. Wei SC, Levine JH, Cogdill AP , Zhao Y, Anang N-AAS, Andrews MC,  et al. Distinct cellular mechanisms underlie anti-CTLA-4 and anti-PD-1  checkpoint blockade. Cell. 2017;170.  44. Kudo M. Durvalumab plus tremelimumab: a novel combination immunotherapy for unresectable hepatocellular carcinoma. Liver Cancer.  2022;11:87–93.  45. Wolchok JD, Saenger Y. The mechanism of anti-CTLA-4 activity and  the negative regulation of T-cell activation. Oncologist. 2008;13(Suppl  4):2–9.  46. Robert L, Tsoi J, Wang X, Emerson R, Homet B, Chodon T, et al. CTLA4  blockade broadens the peripheral T-cell receptor repertoire. Clin Cancer  Res. 2014;20:2424–32.  47.

## 2. 比较型：与单药 PD-1/PD-L1 抑制相比，PD-1/PD-L1 联合 CTLA-4 阻断在作用机制、潜在疗效和免疫相关不良事件方面有哪些差异？

**回答**：

作用机制：双抗联合抑制了PD-PTCL1/PDL1的相互作用，而单抗仅针对PD-CTK4/CTLA4。

潜在疗效：双抗体联合治疗显著提高了肿瘤细胞的杀伤能力，同时减少了对正常组织的损伤，降低了免疫相关副作用的发生率。

免疫相关有害事件：双靶向治疗组的总体反应率（ORR）为42%，而单靶向组仅为22%。然而，双靶标治疗组发生严重的免疫相关毒性事件的比例较低，如发热、疲劳和血小板减少等，这表明双靶标的组合可能具有更好的安全性和耐受性。

- 运行时间：21.521 秒
- source_nodes 数量：3
- 参数：chunk_size=512，chunk_overlap=50，similarity_top_k=3，temperature=0.1

### source_nodes

#### Node 1
- 来源文件：`Cheng_2024_Dual_blockade_PD1_PDL1_CTLA4_lung_cancer.pdf`
- 相似度分数：`0.834138`
- 页码元数据：`21`
- 文本片段：2006;116:1935–45.  42. Simpson TR, Li F, Montalvo-Ortiz W, Sepulveda MA, Bergerhoff K, Arce  F, et al. Fc-dependent depletion of tumor-infiltrating regulatory T cells  co-defines the efficacy of anti-CTLA-4 therapy against melanoma. J Exp  Med. 2013;210:1695–710.  43. Wei SC, Levine JH, Cogdill AP , Zhao Y, Anang N-AAS, Andrews MC,  et al. Distinct cellular mechanisms underlie anti-CTLA-4 and anti-PD-1  checkpoint blockade. Cell. 2017;170.  44. Kudo M. Durvalumab plus tremelimumab: a novel combination immunotherapy for unresectable hepatocellular carcinoma. Liver Cancer.  2022;11:87–93.  45. Wolchok JD, Saenger Y. The mechanism of anti-CTLA-4 activity and  the negative regulation of T-cell activation. Oncologist. 2008;13(Suppl  4):2–9.  46. Robert L, Tsoi J, Wang X, Emerson R, Homet B, Chodon T, et al. CTLA4  blockade broadens the peripheral T-cell receptor repertoire. Clin Cancer  Res. 2014;20:2424–32.  47.

#### Node 2
- 来源文件：`Cheng_2024_Dual_blockade_PD1_PDL1_CTLA4_lung_cancer.pdf`
- 相似度分数：`0.833535`
- 页码元数据：`1`
- 文本片段：org/ licen ses/ by/4. 0/. The Creative Commons Public Domain Dedication waiver (http:// creat iveco  mmons. org/ publi cdoma in/ zero/1. 0/) applies to the data made available in this article, unless otherwise stated in a credit line to the data. Journal of Hematology & Oncology †Weishi Cheng and Kai Kang have contributed equally to this work. *Correspondence: Ailin Zhao zhaoailin@wchscu.cn Yijun Wu wuyj01029@wchscu.cn 1 Division of Thoracic Tumor Multimodality Treatment, Cancer Center,  West China Hospital, Sichuan University, Chengdu, Sichuan, China 2 Peking Union Medical College, Chinese Academy of Medical Sciences,  Beijing, China 3 Laboratory of Clinical Cell Therapy, West China Hospital, Sichuan  University, Chengdu, Sichuan, China 4 Department of Hematology, West China Hospital, Sichuan University,  Chengdu, Sichuan, China

#### Node 3
- 来源文件：`Cheng_2024_Dual_blockade_PD1_PDL1_CTLA4_lung_cancer.pdf`
- 相似度分数：`0.833234`
- 页码元数据：`24`
- 文本片段：Liu E, Marin D, Banerjee P , Macapinlac HA, Thompson P , Basar R, et al.  Use of CAR-transduced natural killer cells in CD19-positive lymphoid  tumors. N Engl J Med. 2020;382:545–53.  168. Harada K, Dong X, Estrella JS, Correa AM, Xu Y, Hofstetter WL, et al.  Tumor-associated macrophage infiltration is highly associated  with PD-L1 expression in gastric adenocarcinoma. Gastric Cancer.  2018;21:31–40.  169. Tsukamoto M, Imai K, Ishimoto T, Komohara Y, Yamashita Y-I, Nakagawa  S, et al. PD-L1 expression enhancement by infiltrating macrophagederived tumor necrosis factor-α leads to poor pancreatic cancer  prognosis. Cancer Sci. 2019;110:310–20.  170. Hodi FS, O’Day SJ, McDermott DF, Weber RW, Sosman JA, Haanen JB,  et al. Improved survival with ipilimumab in patients with metastatic  melanoma. N Engl J Med. 2010;363:711–23.  171. Keir ME, Liang SC, Guleria I, Latchman YE, Qipo A, Albacker LA, et al.  Tissue expression of PD-L1 mediates peripheral T cell tolerance.

## 3. 总结型：根据这些文献，总结免疫检查点抑制剂治疗的主要优势、局限性以及常见免疫相关不良事件，并指出证据来源。

**回答**：

**主要优势：**
1. **免疫检查物抑制剂（ICIs）** 是一种新型的抗肿瘤治疗方法，通过阻断特定的信号通路来抑制肿瘤生长和扩散。
2\. ICIs具有较低的副作用发生率，如感染、胃肠道反应等，且对某些患者来说是安全的。
3\. ICs可以显著改善患者的预后，尤其是对于那些有严重心血管疾病风险的患者。

**局限性：**
- **免疫系统抑制**：ICIs会降低患者的免疫功能，可能导致免疫力下降，增加感染的风险。
- **耐药性**：部分患者可能会因为缺乏有效的治疗方案而发展为耐药状态。
- 长期使用ICIs可能引起一些长期的副作用，包括骨髓抑制、肝肾功能损害等。

**常见免疫相关的不良事件：**
常见的免疫相关事件包括但不限于：
- **感染**：包括肺炎、尿路感染、皮肤感染等。
- 胃肠道反应：恶心、呕吐、腹泻等。
  
**证据来源：**
以上文献均来自医学期刊，其中许多文章提供了详细的病例报告和临床试验数据，以支持其结论。例如，上述文献都引用了来自《柳叶刀》、

- 运行时间：30.705 秒
- source_nodes 数量：3
- 参数：chunk_size=512，chunk_overlap=50，similarity_top_k=3，temperature=0.1

### source_nodes

#### Node 1
- 来源文件：`Yin_2023_Immune_related_adverse_events.pdf`
- 相似度分数：`0.724459`
- 页码元数据：`16`
- 文本片段：Smolen JS, Landewe R, Bergstra SA, Kerschbaumer A, Sepriano A, Aletaha D, et al. EULAR recommendations for the management of rheumatoid arthritis with synthetic and biological disease-modifying antirheumatic drugs: 2022 update.Ann Rheum Dis(2023) 82:3– 18. doi:10.1136/ard-2022-223356 139. Stone JH, Tuckwell K, Dimonaco S, Klearman M, Aringer M, Blockmans D, et al. Trial of tocilizumab in giant-cell arteritis.N Engl J Med (2017) 377:317– 28. doi: 10.1056/NEJMoa1613849 140. Stroud CR, Hegde A, Cherry C, Naqash AR, Sharma N, Addepalli S, et al. Tocilizumab for the management of immune mediated adverse events secondary to PD-1 blockade.J Oncol Pharm Pract(2019) 25:551– 7. doi:10.1177/1078155217745144 141. Horisberger A, La Rosa S, Zurcher JP, Zimmermann S, Spertini F, Coukos G, et al.

#### Node 2
- 来源文件：`Yin_2023_Immune_related_adverse_events.pdf`
- 相似度分数：`0.71943`
- 页码元数据：`15`
- 文本片段：Cuzzubbo S, Javeri F, Tissier M, Roumi A, Barlog C, Doridam J, et al. Neurological adverse events associated with immune checkpoint inhibitors: review of the literature.Eur J Cancer(2017) 73:1– 8. doi:10.1016/j.ejca.2016.12.001 98. Marini A, Bernardini A, Gigli GL, Valente M, Muniz-Castrillo S, Honnorat J, et al. Neurologic adverse events of immune checkpoint inhibitors: a systematic review. Neurology (2021) 96:754– 66. doi:10.1212/WNL.0000000000011795 99. Varricchi G, Galdiero MR, Marone G, Criscuolo G, Triassi M, Bonaduce D, et al. Cardiotoxicity of immune checkpoint inhibitors. ESMO Open (2017) 2:e247. doi: 10.1136/esmoopen-2017-000247 100. Cardinale D, Sandri MT, Colombo A, Colombo N, Boeri M, Lamantia G, et al. Prognostic value of troponin I in cardiac risk strati fication of cancer patients undergoing high-dose chemotherapy. Circulation (2004) 109:2749– 54. doi: 10.1161/ 01.CIR.0000130926.51766.CC 101.

#### Node 3
- 来源文件：`Yin_2023_Immune_related_adverse_events.pdf`
- 相似度分数：`0.716356`
- 页码元数据：`15`
- 文本片段：doi:10.1136/jitc-2021-002435 Yin et al. 10.3389/fimmu.2023.1167975 Frontiers inImmunology frontiersin.org15

## 4. 证据不足测试：仅根据当前本地文献库，能否准确预测某一位具体患者接受纳武利尤单抗后的个人生存月数？请说明理由。

**回答**：

现有文献无此信息。

- 运行时间：4.243 秒
- source_nodes 数量：3
- 参数：chunk_size=512，chunk_overlap=50，similarity_top_k=3，temperature=0.1

### source_nodes

#### Node 1
- 来源文件：`Yin_2023_Immune_related_adverse_events.pdf`
- 相似度分数：`0.662834`
- 页码元数据：`15`
- 文本片段：doi:10.1136/jitc-2021-002435 Yin et al. 10.3389/fimmu.2023.1167975 Frontiers inImmunology frontiersin.org15

#### Node 2
- 来源文件：`Yin_2023_Immune_related_adverse_events.pdf`
- 相似度分数：`0.659332`
- 页码元数据：`11`
- 文本片段：Yin et al. 10.3389/fimmu.2023.1167975 Frontiers inImmunology frontiersin.org11

#### Node 3
- 来源文件：`Yin_2023_Immune_related_adverse_events.pdf`
- 相似度分数：`0.658185`
- 页码元数据：`17`
- 文本片段：Glossary ACTH adrenocorticotropic hormone AKI acute kidney injury ALT alanine aminotransferase APCs antigen presenting cells AST aspartate aminotransferase BCC basal cell carcinoma BD Bullous dermatitis BRCA bladder urothelial carcinoma CC cervical cancer cHL classical Hodgkin ’s lymphoma CRC colorectal cancer CSCC cutaneous squamous cell carcinoma CTCAE the Common Terminology Criteria for Adverse Events CTLA-4 cytotoxic T lymphocyte-associated antigen 4 DKA diabetic ketoacidosis dMMR mismatch repair de ficiency EC endometrial carcinoma ECG electrocardiograph EMA European Medicines Agency ESCC esophageal squamous cell carcinoma FDA the United States Food and Drug Administration FBG fasting blood-glucose GC gastric cancer GEP gene expression profile HC Health Canada HCC hepatocellular carcinoma HL Hodgkin’s lymphoma HLH Hemophagocytic lymphohistiocytosis HNSCC head and neck squamous cell carcinoma ICIs immune checkpoint inhibitors IMH immune-mediated hepatotoxicity irCAEs cutaneous immune-related adverse events irAEs immune-related adverse events IO immune-oncologic IV intravenous LAG-3 lymphocyte-activation gene 3 LFTs liver function-test MCC Merkel cell carcinoma (Continued) Continued MHLW Ministry of Health,
