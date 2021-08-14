interface Serializable<T> {
    deserialize(input: any): T;
}
export declare class Recovery implements Serializable<Recovery> {
    disease: number;
    firstPositiveTestDate: string;
    country: string;
    issuer: string;
    validFrom: string;
    validUntil: string;
    uvci: string;
    deserialize(input: any): Recovery;
}
export declare class Test implements Serializable<Test> {
    disease: number;
    type: string;
    name: string;
    device: string;
    date: string;
    result: number;
    facility: string;
    country: string;
    issuer: string;
    uvci: string;
    deserialize(input: any): Test;
}
export declare class Vaccination implements Serializable<Vaccination> {
    disease: number;
    prophylaxis: number;
    vaccineProduct: string;
    manufacturer: string;
    doseNumber: number;
    overallDoses: number;
    date: string;
    country: string;
    issuer: string;
    uvci: string;
    deserialize(input: any): Vaccination;
}
export declare class Name implements Serializable<Name> {
    familyName: string;
    givenName: string;
    familyNameNormalized: string;
    givenNameNormalized: string;
    getFullName(): string;
    getFullNameNormalized(): string;
    deserialize(input: any): Name;
}
export declare class Hcert implements Serializable<Hcert> {
    version: string;
    dob: string;
    name: Name | undefined;
    vaccination: Vaccination | undefined;
    test: Test | undefined;
    recovery: Recovery | undefined;
    deserialize(input: any): Hcert;
}
export default class DCC implements Serializable<DCC> {
    valid: boolean;
    issuerCountry: string;
    issueDate: number;
    expirationDate: number;
    certificates: Hcert[];
    deserialize(input: any): DCC;
}
export {};
