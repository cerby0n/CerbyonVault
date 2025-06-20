import React, { useState, useEffect } from "react";
import useAxios from "../axios/useAxios";
import dayjs from "dayjs";
import { IoWarning } from "react-icons/io5";
import { AiFillSafetyCertificate } from "react-icons/ai";
import { BsFileEarmarkExcelFill, BsFileEarmarkCheckFill } from "react-icons/bs";
import { useNavigate } from "react-router-dom";

type StatKey = "expired" | "valid" | "expiring";

const daysOptions = [7, 30];

type Certificate = {
  id: number;
  name: string;
  subject: string;
  not_after: string;
};

type StatConfig = {
  key: StatKey;
  title: string;
  icon: React.ReactNode;
  value?: number;
  loading: boolean;
};

export const DashboardStats: React.FC = () => {
  const axios = useAxios();

  const [overview, setOverview] = useState<{
    total_certificates: number;
    expired_certificates: number;
    valid_certificates: number;
  } | null>(null);
  const [loadingOverview, setLoadingOverview] = useState(true);
  const [loadingExpiring, setLoadingExpiring] = useState(true);
  const [loadingTopExpiry, setLoadingTopExpiry] = useState(true);
  const [loadingList, setLoadingList] = useState(false);

  // For showing certificate list
  const [days, setDays] = useState(daysOptions[1]);
  const [selectedStat, setSelectedStat] = useState<StatKey | null>(null);
  const [certificates, setCertificates] = useState<Certificate[]>([]);
  const [expiringSoon, setExpiringSoon] = useState<number | null>(null);
  const [topExpiry, setTopExpiry] = useState<Certificate[]>([]);

  useEffect(() => {
    if (!selectedStat) return;
    setLoadingList(true);
    let url = "/dashboard/certificates-list/?type=" + selectedStat;
    if (selectedStat === "expiring") {
      url += `&days=${days}`;
    }
    axios
      .get(url)
      .then((res) => setCertificates(Array.isArray(res.data) ? res.data : []))
      .catch(() => setCertificates([]))
      .finally(() => setLoadingList(false));
  }, [selectedStat, days]);

  useEffect(() => {
    setLoadingTopExpiry(true);
    axios
      .get("/dashboard/certificates-top-expiry/?limit=20")
      .then((res) => setTopExpiry(Array.isArray(res.data) ? res.data : []))
      .catch(() => setTopExpiry([]))
      .finally(() => setLoadingTopExpiry(false));
  }, []);

  useEffect(() => {
    setLoadingOverview(true);
    axios
      .get("/dashboard/certificates-overview/")
      .then((res) => setOverview(res.data))
      .catch(() => setOverview(null))
      .finally(() => setLoadingOverview(false));
  }, []);

  useEffect(() => {
    setLoadingExpiring(true);
    axios
      .get(`/dashboard/certificates-expiring-soon/?days=${days}`)
      .then((res) => setExpiringSoon(res.data.expiring_soon_certificates))
      .catch(() => setExpiringSoon(null))
      .finally(() => setLoadingExpiring(false));
  }, [days]);

  const stats: StatConfig[] = [
    {
      key: "valid",
      title: "Valid Certificates",
      icon: <BsFileEarmarkCheckFill className="text-success" />,
      value: overview?.valid_certificates,
      loading: loadingOverview,
    },
    {
      key: "expired",
      title: "Expired Certificates",
      icon: <BsFileEarmarkExcelFill className="text-error" />,
      value: overview?.expired_certificates,
      loading: loadingOverview,
    },
    {
      key: "expiring",
      title: `Expiring in ${days} days`,
      icon: <IoWarning className="text-warning text-4xl" />,
      value: expiringSoon ?? undefined,
      loading: loadingExpiring,
    },
  ];

  // Toggle: Clicking the same tile closes the table
  function handleStatClick(key: StatKey) {
    setSelectedStat((prev) => (prev === key ? null : key));
  }

  return (
    <div className="w-full flex flex-col">
      <div className="p-6 bg-base-100 rounded top-0 items-center mb-2">
        <h1 className="text-4xl font-bold text-secondary-content">Dashboard</h1>
      </div>
      <div className=" flex-1 flex flex-col bg-base-100 p-4 rounded shadow space-y-4">
        <div className="grid gap-4 grid-cols-1">
          <StatCard
            title="Total Certificates"
            icon={<AiFillSafetyCertificate size={40} className="text-accent" />}
            value={overview?.total_certificates}
            loading={loadingOverview}
            onClick={() => setSelectedStat(null)}
          />
        </div>
        <div className="grid gap-4 grid-cols-1 md:grid-cols-3">
          {stats.map((stat) => (
            <StatCard
              key={stat.key}
              title={stat.title}
              value={stat.value}
              loading={stat.loading}
              icon={stat.icon}
              onClick={() => handleStatClick(stat.key)}
              active={selectedStat === stat.key}
              pill={
                stat.key === "expiring" ? (
                  <div className="flex gap-2 ml-2">
                    {[7, 30].map((d) => (
                      <button
                        key={d}
                        type="button"
                        className={`px-3 py-1 rounded-full text-xs font-semibold 
              ${
                days === d
                  ? "bg-warning text-warning-content font-bold"
                  : "bg-neutral/10 text-neutral hover:bg-warning hover:text-warning-content"
              }`}
                        onClick={(e) => {
                          e.stopPropagation();
                          setDays(d);
                          if (selectedStat !== "expiring") {
                            setSelectedStat("expiring");
                          }
                        }}
                      >
                        {d} days
                      </button>
                    ))}
                  </div>
                ) : undefined
              }
            />
          ))}
        </div>
        {/* Certificate Table below grid */}
        <div className="flex-1 flex flex-col bg-base-100 rounded shadow-md border border-neutral/15 p-6 w-full">
          {selectedStat ? (
            <>
              <h2 className="text-2xl text-secondary-content font-bold mb-4">
                {stats.find((s) => s.key === selectedStat)?.title}
              </h2>
              {loadingList ? (
                <div className="flex justify-center items-center min-h-[70px]">
                  <span className="loading loading-dots loading-xl"></span>
                </div>
              ) : certificates.length === 0 ? (
                <p className="text-center">No certificates found.</p>
              ) : (
                <CertificateTable certificates={certificates} />
              )}
            </>
          ) : (
            <>
              <h2 className="text-2xl text-secondary-content font-bold mb-4">
                Top 20 by Nearest Expiry
              </h2>
              {loadingTopExpiry ? (
                <div className="flex justify-center items-center min-h-[70px]">
                  <span className="loading loading-dots loading-xl"></span>
                </div>
              ) : topExpiry.length === 0 ? (
                <p className="text-center">No certificates found.</p>
              ) : (
                <CertificateTable certificates={topExpiry} />
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

interface StatCardProps {
  title: string;
  value?: number;
  loading: boolean;
  icon: React.ReactNode;
  onClick?: () => void;
  active?: boolean;
  pill?: React.ReactNode;
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  loading,
  icon,
  onClick,
  active,
  pill,
}) => (
  <div
    onClick={onClick}
    className={`flex flex-col border border-neutral/15 rounded p-6 bg-base-100 shadow cursor-pointer transition-all duration-200 hover:bg-accent/5 ${
      active ? "ring-2 ring-accent/50" : ""
    }`}
  >
    <div className=" flex mb-5 justify-between">
      <div className="flex gap-2">
        <span className="text-3xl">{icon}</span>
        <span className="text-2xl font-semibold text-secondary-content">
          {title}
        </span>
      </div>
      <div>{pill}</div>
    </div>
    <span className="text-5xl font-bold">{loading ? "..." : value}</span>
  </div>
);

interface CertificateTableProps {
  certificates: Certificate[];
  dateFormat?: string;
}

const CertificateTable: React.FC<CertificateTableProps> = ({
  certificates=[],
  dateFormat = "DD MMM YYYY",
}) => {
  const navigate = useNavigate();

  const handleRowClick = (cert: Certificate) => {
    navigate("/certificates", { state: { selectedCertId: cert.id } });
  };
  return (
    <div className="overflow-x-auto">
      <table className="table table-pin-rows">
        <thead className="">
          <tr>
            <th>Name</th>
            <th>Subject</th>
            <th className="text-end">Expires On</th>
          </tr>
        </thead>
        <tbody>
          {certificates.map((cert) => (
            <tr
              key={cert.id}
              className="cursor-pointer hover:bg-primary/10"
              onClick={() => handleRowClick(cert)}
            >
              <td className="truncate">{cert.name}</td>
              <td className="truncate">{cert.subject}</td>
              <td className="truncate text-end">
                {dayjs(cert.not_after).isValid()
                  ? dayjs(cert.not_after).format(dateFormat)
                  : cert.not_after}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
export default DashboardStats;
