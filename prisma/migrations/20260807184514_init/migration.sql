-- CreateEnum
CREATE TYPE "ContactKind" AS ENUM ('LEAD', 'TENANT', 'LANDLORD', 'CONTRACTOR');

-- CreateEnum
CREATE TYPE "PropertyStatus" AS ENUM ('AVAILABLE', 'UNDER_OFFER', 'LET', 'OFF_MARKET');

-- CreateEnum
CREATE TYPE "ViewingSlotStatus" AS ENUM ('OPEN', 'BOOKED', 'CANCELLED');

-- CreateEnum
CREATE TYPE "Channel" AS ENUM ('EMAIL', 'SMS', 'WHATSAPP', 'INTERNAL');

-- CreateEnum
CREATE TYPE "Direction" AS ENUM ('INBOUND', 'OUTBOUND');

-- CreateEnum
CREATE TYPE "Workflow" AS ENUM ('LEAD', 'MAINTENANCE', 'ARREARS', 'COMPLIANCE', 'GENERAL');

-- CreateEnum
CREATE TYPE "MaintenanceUrgency" AS ENUM ('EMERGENCY', 'URGENT', 'ROUTINE');

-- CreateEnum
CREATE TYPE "MaintenanceStatus" AS ENUM ('NEW', 'ACKNOWLEDGED', 'CONTRACTOR_ASSIGNED', 'IN_PROGRESS', 'RESOLVED');

-- CreateEnum
CREATE TYPE "ArrearsStage" AS ENUM ('REMINDER_1', 'REMINDER_2', 'FORMAL_NOTICE', 'ESCALATED', 'RESOLVED');

-- CreateEnum
CREATE TYPE "ComplianceType" AS ENUM ('GAS_SAFETY', 'EICR', 'EPC', 'DEPOSIT_PROTECTION', 'RIGHT_TO_RENT');

-- CreateEnum
CREATE TYPE "ComplianceStatus" AS ENUM ('VALID', 'DUE_SOON', 'OVERDUE', 'RESOLVED');

-- CreateEnum
CREATE TYPE "ActionStatus" AS ENUM ('PENDING', 'APPROVED', 'REJECTED', 'SENT', 'FAILED');

-- CreateTable
CREATE TABLE "Contact" (
    "id" TEXT NOT NULL,
    "kind" "ContactKind" NOT NULL,
    "name" TEXT NOT NULL,
    "email" TEXT,
    "phone" TEXT,
    "whatsappOptIn" BOOLEAN NOT NULL DEFAULT false,
    "notes" TEXT,
    "mondayItemId" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Contact_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Property" (
    "id" TEXT NOT NULL,
    "addressLine1" TEXT NOT NULL,
    "addressLine2" TEXT,
    "city" TEXT NOT NULL,
    "postcode" TEXT NOT NULL,
    "bedrooms" INTEGER,
    "rentPcm" INTEGER,
    "status" "PropertyStatus" NOT NULL DEFAULT 'AVAILABLE',
    "landlordId" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Property_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Tenancy" (
    "id" TEXT NOT NULL,
    "propertyId" TEXT NOT NULL,
    "tenantId" TEXT NOT NULL,
    "startDate" TIMESTAMP(3) NOT NULL,
    "endDate" TIMESTAMP(3),
    "rentDueDay" INTEGER NOT NULL,
    "rentPcm" INTEGER NOT NULL,
    "depositProtected" BOOLEAN NOT NULL DEFAULT false,
    "active" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Tenancy_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ViewingSlot" (
    "id" TEXT NOT NULL,
    "propertyId" TEXT NOT NULL,
    "startsAt" TIMESTAMP(3) NOT NULL,
    "endsAt" TIMESTAMP(3) NOT NULL,
    "status" "ViewingSlotStatus" NOT NULL DEFAULT 'OPEN',
    "bookedById" TEXT,
    "mondayItemId" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "ViewingSlot_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Message" (
    "id" TEXT NOT NULL,
    "contactId" TEXT,
    "channel" "Channel" NOT NULL,
    "direction" "Direction" NOT NULL,
    "workflow" "Workflow" NOT NULL DEFAULT 'GENERAL',
    "subject" TEXT,
    "body" TEXT NOT NULL,
    "externalId" TEXT,
    "threadId" TEXT,
    "relatedType" TEXT,
    "relatedId" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Message_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "MaintenanceTicket" (
    "id" TEXT NOT NULL,
    "propertyId" TEXT NOT NULL,
    "tenantId" TEXT NOT NULL,
    "category" TEXT NOT NULL,
    "urgency" "MaintenanceUrgency" NOT NULL,
    "description" TEXT NOT NULL,
    "status" "MaintenanceStatus" NOT NULL DEFAULT 'NEW',
    "contractorId" TEXT,
    "mondayItemId" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "MaintenanceTicket_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ArrearsCase" (
    "id" TEXT NOT NULL,
    "tenancyId" TEXT NOT NULL,
    "amountOwedPence" INTEGER NOT NULL,
    "daysOverdue" INTEGER NOT NULL DEFAULT 0,
    "stage" "ArrearsStage" NOT NULL DEFAULT 'REMINDER_1',
    "lastActionAt" TIMESTAMP(3),
    "mondayItemId" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "ArrearsCase_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ComplianceItem" (
    "id" TEXT NOT NULL,
    "propertyId" TEXT NOT NULL,
    "type" "ComplianceType" NOT NULL,
    "dueDate" TIMESTAMP(3) NOT NULL,
    "status" "ComplianceStatus" NOT NULL DEFAULT 'VALID',
    "mondayItemId" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "ComplianceItem_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Action" (
    "id" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "workflow" "Workflow" NOT NULL,
    "autoSend" BOOLEAN NOT NULL,
    "status" "ActionStatus" NOT NULL DEFAULT 'PENDING',
    "channel" "Channel" NOT NULL,
    "contactId" TEXT,
    "relatedType" TEXT,
    "relatedId" TEXT,
    "subject" TEXT,
    "body" TEXT NOT NULL,
    "reasoning" TEXT,
    "decidedBy" TEXT,
    "decidedAt" TIMESTAMP(3),
    "sentAt" TIMESTAMP(3),
    "error" TEXT,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Action_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "StaffUser" (
    "id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "StaffUser_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "Contact_kind_idx" ON "Contact"("kind");

-- CreateIndex
CREATE INDEX "Contact_email_idx" ON "Contact"("email");

-- CreateIndex
CREATE INDEX "Contact_phone_idx" ON "Contact"("phone");

-- CreateIndex
CREATE INDEX "Property_status_idx" ON "Property"("status");

-- CreateIndex
CREATE INDEX "Tenancy_propertyId_idx" ON "Tenancy"("propertyId");

-- CreateIndex
CREATE INDEX "Tenancy_tenantId_idx" ON "Tenancy"("tenantId");

-- CreateIndex
CREATE INDEX "ViewingSlot_propertyId_status_idx" ON "ViewingSlot"("propertyId", "status");

-- CreateIndex
CREATE INDEX "Message_contactId_idx" ON "Message"("contactId");

-- CreateIndex
CREATE INDEX "Message_threadId_idx" ON "Message"("threadId");

-- CreateIndex
CREATE INDEX "Message_workflow_idx" ON "Message"("workflow");

-- CreateIndex
CREATE INDEX "MaintenanceTicket_status_idx" ON "MaintenanceTicket"("status");

-- CreateIndex
CREATE INDEX "MaintenanceTicket_urgency_idx" ON "MaintenanceTicket"("urgency");

-- CreateIndex
CREATE INDEX "ArrearsCase_stage_idx" ON "ArrearsCase"("stage");

-- CreateIndex
CREATE INDEX "ComplianceItem_status_idx" ON "ComplianceItem"("status");

-- CreateIndex
CREATE INDEX "ComplianceItem_dueDate_idx" ON "ComplianceItem"("dueDate");

-- CreateIndex
CREATE INDEX "Action_status_idx" ON "Action"("status");

-- CreateIndex
CREATE INDEX "Action_workflow_idx" ON "Action"("workflow");

-- CreateIndex
CREATE UNIQUE INDEX "StaffUser_email_key" ON "StaffUser"("email");

-- AddForeignKey
ALTER TABLE "Property" ADD CONSTRAINT "Property_landlordId_fkey" FOREIGN KEY ("landlordId") REFERENCES "Contact"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Tenancy" ADD CONSTRAINT "Tenancy_propertyId_fkey" FOREIGN KEY ("propertyId") REFERENCES "Property"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Tenancy" ADD CONSTRAINT "Tenancy_tenantId_fkey" FOREIGN KEY ("tenantId") REFERENCES "Contact"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ViewingSlot" ADD CONSTRAINT "ViewingSlot_propertyId_fkey" FOREIGN KEY ("propertyId") REFERENCES "Property"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ViewingSlot" ADD CONSTRAINT "ViewingSlot_bookedById_fkey" FOREIGN KEY ("bookedById") REFERENCES "Contact"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Message" ADD CONSTRAINT "Message_contactId_fkey" FOREIGN KEY ("contactId") REFERENCES "Contact"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "MaintenanceTicket" ADD CONSTRAINT "MaintenanceTicket_propertyId_fkey" FOREIGN KEY ("propertyId") REFERENCES "Property"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "MaintenanceTicket" ADD CONSTRAINT "MaintenanceTicket_tenantId_fkey" FOREIGN KEY ("tenantId") REFERENCES "Contact"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "MaintenanceTicket" ADD CONSTRAINT "MaintenanceTicket_contractorId_fkey" FOREIGN KEY ("contractorId") REFERENCES "Contact"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ArrearsCase" ADD CONSTRAINT "ArrearsCase_tenancyId_fkey" FOREIGN KEY ("tenancyId") REFERENCES "Tenancy"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ComplianceItem" ADD CONSTRAINT "ComplianceItem_propertyId_fkey" FOREIGN KEY ("propertyId") REFERENCES "Property"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Action" ADD CONSTRAINT "Action_contactId_fkey" FOREIGN KEY ("contactId") REFERENCES "Contact"("id") ON DELETE SET NULL ON UPDATE CASCADE;

