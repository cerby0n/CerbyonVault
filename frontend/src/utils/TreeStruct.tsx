import { Certificate } from "../types";

export type CertificateNode = Certificate & {
  children: CertificateNode[];
};

export function buildCertificateTree(certs: Certificate[]): CertificateNode[] {
  const certMap = new Map<number, CertificateNode>();

  if (!Array.isArray(certs)) {
    console.error("Expected array, got:", certs);
    return [];
  }

  certs.forEach(cert => {
    certMap.set(cert.id, { ...cert, children: [] });
  });

  const roots: CertificateNode[] = [];

  certs.forEach(cert => {
    if (cert.parent && cert.parent !== cert.id) {
      // Cert has a parent, add it to the parent's children
      const parent = certMap.get(cert.parent);
      if (parent) {
        parent.children.push(certMap.get(cert.id)!);
      }
    } else {
      // Cert has no parent, it's a root certificate
      roots.push(certMap.get(cert.id)!);
    }
  });

  return roots
}
