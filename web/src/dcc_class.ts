
interface Serializable<T> {
    deserialize(input: any): T;
}

export class Recovery implements Serializable<Recovery> {
    disease: number = 0;
    firstPositiveTestDate: string = "";
    country: string = "";
    issuer: string = "";
    validFrom: string = "";
    validUntil: string = "";
    uvci: string = "";


    deserialize(input: any): Recovery {

        this.disease = +input.tg;
        this.firstPositiveTestDate = input.fr;
        this.country = input.co;
        this.issuer = input.is;
        this.validFrom = input.df;
        this.validUntil = input.du;
        this.uvci = input.ci;
        return this;
    }
}

export class Test implements Serializable<Test> {
    disease: number = 0;
    type: string = "";
    name: string = "";
    device: string = "";
    date: string = "";
    result: number = 0;
    facility: string = "";
    country: string = "";
    issuer: string = "";
    uvci: string = "";

    deserialize(input: any): Test {
        this.disease = +input.tg;
        this.type = input.tt;
        this.name = input.nm;
        this.device = input.ma;
        this.date = input.sc;
        this.result = +input.tr;
        this.facility = input.tc;
        this.country = input.co;
        this.issuer = input.is;
        this.uvci = input.ci;
        return this;
    }
}

export class Vaccination implements Serializable<Vaccination> {
    disease: number = 0;
    prophylaxis: number = 0;
    vaccineProduct: string = "";
    manufacturer: string = "";
    doseNumber: number = 0;
    overallDoses: number = 0;
    date: string = "";
    country: string = "";
    issuer: string = "";
    uvci: string = "";


    deserialize(input: any): Vaccination {
        this.disease = +input.tg;
        this.prophylaxis = +input.vp;
        this.vaccineProduct = input.mp;
        this.manufacturer = input.ma;
        this.doseNumber = input.dn;
        this.overallDoses = input.sd;
        this.date = input.dt;
        this.country = input.co;
        this.issuer = input.is;
        this.uvci = input.ci;

        return this;
    }
}

export class Name implements Serializable<Name> {
    familyName: string = "";
    givenName: string = "";
    familyNameNormalized: string = "";
    givenNameNormalized: string = "";

    getFullName(): string {
        let fullname: string = this.givenName + " " + this.familyName;
        return fullname
    }
    getFullNameNormalized(): string {
        let fullname: string = this.givenNameNormalized + " " + this.familyNameNormalized;
        return fullname
    }

    deserialize(input: any): Name {
        this.familyName = input.fn;
        this.familyNameNormalized = input.fnt;
        if (typeof input.gn !== undefined) {
            this.givenName = input.gn;
        }
        if (typeof input.gnt !== undefined) {
            this.givenNameNormalized = input.gnt;
        }
        return this;
    }
}

export class Hcert implements Serializable<Hcert> {
    version: string = "";
    dob: string = "";
    name: Name | undefined;
    vaccination: Vaccination | undefined;
    test: Test | undefined;
    recovery: Recovery | undefined;

    deserialize(input: any): Hcert {
        this.version = input.ver;
        this.dob = input.dob;
        this.name = new Name().deserialize(input.nam)
        if (typeof input.v !== undefined) {
            this.vaccination = new Vaccination().deserialize(input.v[0]);
        } else if (typeof input.t !== undefined) {
            this.test = new Test().deserialize(input.t[0]);
        } else if (typeof input.r !== undefined) {
            this.recovery = new Recovery().deserialize(input.r[0]);
        }
        return this;
    }
}

export default class DCC implements Serializable<DCC> {
    valid: boolean = false;
    issuerCountry: string = "";
    issueDate: number = 0;
    expirationDate: number = 0;
    certificates: Hcert[] = [];


    deserialize(input: any): DCC {
        this.valid = input.valid;
        this.issuerCountry = input.dccdata["1"];
        this.issueDate = input.dccdata["6"];
        this.expirationDate = input.dccdata["4"];
        const hcerts: any = input.dccdata["-260"];
        for (let key in hcerts) {
            let hcert_raw: any = hcerts[key]
            let hcert = new Hcert().deserialize(hcert_raw);
            this.certificates.push(hcert);
        }
        return this;
    }

}