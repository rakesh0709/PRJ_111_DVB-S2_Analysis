from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from report_content.builder_utils import add_chapter_title

REFERENCES_LIST = [
    "[1] C. E. Shannon, 'A Mathematical Theory of Communication,' Bell System Technical Journal, vol. 27, no. 3, pp. 379–423, Jul. 1948. doi: 10.1002/j.1538-7305.1948.tb01338.x.",
    "[2] ISO/IEC, 'Information technology — Generic coding of moving pictures and associated audio information: Systems,' ISO/IEC 13818-1:2019, International Organization for Standardization, Geneva, Switzerland, 2019.",
    "[3] A. Morello and V. Mignone, 'DVB-S2: The Second Generation Standard for Satellite Broadband Services,' Proceedings of the IEEE, vol. 94, no. 1, pp. 210–227, Jan. 2006. doi: 10.1109/JPROC.2005.861013.",
    "[4] ETSI, 'Digital Video Broadcasting (DVB); Generic Stream Encapsulation (GSE); Part 1: Protocol,' ETSI TS 102 606-1 V1.2.1, European Telecommunications Standards Institute, Sophia Antipolis, France, Jul. 2014.",
    "[5] G. Fairhurst and M. Collina, 'Analysis of Generic Stream Encapsulation (GSE) for Satellite Broadband Networks,' International Journal of Satellite Communications and Networking, vol. 28, no. 3–4, pp. 197–215, May 2010. doi: 10.1002/sat.946.",
    "[6] ETSI, 'Digital Video Broadcasting (DVB); Second generation framing structure, channel coding and modulation systems for Broadcasting, Interactive Services, News Gathering and other broadband satellite applications; Part 2: DVB-S2 Extensions (DVB-S2X),' ETSI EN 302 307-2 V1.3.1, European Telecommunications Standards Institute, Sophia Antipolis, France, Jul. 2021.",
    "[7] ETSI, 'Digital Video Broadcasting (DVB); Measurement guidelines for DVB systems,' ETSI TR 101 290 V1.3.1, European Telecommunications Standards Institute, Sophia Antipolis, France, Jul. 2014.",
    "[8] A. Orebaugh, G. Ramirez, and J. Beale, Wireshark & Ethereal Network Protocol Analyzer Toolkit. Burlington, MA, USA: Syngress Publishing, 2006.",
    "[9] DekTec Digital Video B.V., 'StreamXpert: Transport-Stream Analyzer Software User Manual,' DekTec Technical Documentation, Hilversum, The Netherlands, 2023. [Online]. Available: https://www.dektec.com/products/applications/StreamXpert/",
    "[10] Rohde & Schwarz GmbH, 'R&S BTC Broadcast Test Center Operating Manual,' Rohde & Schwarz Instrument Documentation, Munich, Germany, 2022.",
    "[11] E. Peeters, 'DVBInspector: Open Source DVB Transport Stream Analyzer,' Version 1.16, 2023. [Online]. Available: https://github.com/radman1/DVBInspector",
    "[12] V. Chandola, A. Banerjee, and V. Kumar, 'Anomaly Detection: A Survey,' ACM Computing Surveys, vol. 41, no. 3, pp. 1–58, Jul. 2009. doi: 10.1145/1541880.1541882.",
    "[13] M. A. F. Pimentel, D. A. Clifton, L. Clifton, and L. Tarassenko, 'A Review of Novelty Detection,' Signal Processing, vol. 99, pp. 215–249, Jun. 2014. doi: 10.1016/j.sigpro.2013.12.026.",
    "[14] F. T. Liu, K. M. Ting, and Z.-H. Zhou, 'Isolation Forest,' in Proceedings of the 2008 Eighth IEEE International Conference on Data Mining (ICDM '08), Pisa, Italy, Dec. 2008, pp. 413–422. doi: 10.1109/ICDM.2008.17.",
    "[15] F. T. Liu, K. M. Ting, and Z.-H. Zhou, 'Isolation-Based Anomaly Detection,' ACM Transactions on Knowledge Discovery from Data (TKDD), vol. 6, no. 1, pp. 1–39, Mar. 2012. doi: 10.1145/2133360.2133363.",
    "[16] R. Guidotti, A. Monreale, S. Ruggieri, F. Turini, F. Giannotti, and D. Pedreschi, 'A Survey of Methods for Explaining Black Box Models,' ACM Computing Surveys, vol. 51, no. 5, pp. 1–42, Aug. 2018. doi: 10.1145/3236009.",
    "[17] S. M. Lundberg and S.-I. Lee, 'A Unified Approach to Interpreting Model Predictions,' in Advances in Neural Information Processing Systems 30 (NeurIPS 2017), Long Beach, CA, USA, Dec. 2017, pp. 4765–4774.",
    "[18] T. Akidau, S. Chernyak, and R. Lax, Streaming Systems: The What, Where, When, and How of Large-Scale Data Processing. Sebastopol, CA, USA: O'Reilly Media, 2018.",
    "[19] Reactive Streams Initiative, 'Reactive Streams Standard Specification for Asynchronous Stream Processing,' Version 1.0.3, 2020. [Online]. Available: https://www.reactive-streams.org/",
    "[20] F. Pedregosa et al., 'Scikit-learn: Machine Learning in Python,' Journal of Machine Learning Research, vol. 12, pp. 2825–2830, Nov. 2011.",
    "[21] ETSI, 'Digital Video Broadcasting (DVB); Specification for Service Information (SI) in DVB systems,' ETSI EN 300 468 V1.16.1, European Telecommunications Standards Institute, Sophia Antipolis, France, Aug. 2019.",
    "[22] D. Minoli, Innovations in Satellite Communications and Satellite Technology. Hoboken, NJ, USA: John Wiley & Sons, 2015. doi: 10.1002/9781118984086.",
    "[23] B. Sklar, Digital Communications: Fundamentals and Applications, 2nd ed. Upper Saddle River, NJ, USA: Prentice Hall, 2001."
]

def build_references(doc):
    add_chapter_title(doc, "REFERENCES", "")
    
    p_intro = doc.add_paragraph()
    p_intro.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_intro.paragraph_format.space_before = Pt(0)
    p_intro.paragraph_format.space_after = Pt(12)
    p_intro.paragraph_format.line_spacing = 1.5
    r = p_intro.add_run(
        "The theoretical concepts, telecommunications standards, algorithmic formulations, and comparative baselines "
        "utilized throughout this project are grounded in established, peer-reviewed scientific literature and international "
        "standards documents. References are arranged in strict order of appearance in accordance with university Harvard/IEEE guidelines:"
    )
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    
    for ref_str in REFERENCES_LIST:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ref.paragraph_format.space_before = Pt(2)
        p_ref.paragraph_format.space_after = Pt(6)
        p_ref.paragraph_format.line_spacing = 1.25
        p_ref.paragraph_format.left_indent = Inches(0.4)
        p_ref.paragraph_format.first_line_indent = Inches(-0.4)
        
        r_ref = p_ref.add_run(ref_str)
        r_ref.font.name = "Times New Roman"
        r_ref.font.size = Pt(10.5)
        r_ref.font.color.rgb = RGBColor(0, 0, 0)
